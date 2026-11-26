import io
import json
import openpyxl
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from core.agent_core import agente_service

router = APIRouter()


def _invocar_agente(prompt: str, session_id: str = "excel_formula") -> str:
    for attr in ("responder", "chat", "run", "procesar"):
        fn = getattr(agente_service, attr, None)
        if callable(fn):
            try:
                res = fn(prompt, session_id=session_id)
            except TypeError:
                res = fn(prompt)
            if isinstance(res, dict):
                return str(res.get("reply") or res.get("response") or res.get("output") or "")
            return str(res or "")
    raise RuntimeError("No se encontró un método compatible en agente_service.")


@router.post("/soporte/excel")
async def aplicar_formula_excel(
    file: UploadFile = File(...),
    instruction: str = Form(...)
):
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Solo se admiten archivos .xlsx")

    content = await file.read()
    try:
        wb = openpyxl.load_workbook(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"No se pudo leer el archivo Excel: {exc}")

    ws = wb.active

    muestra = []
    for r in range(1, min(ws.max_row + 1, 8)):
        muestra.append([ws.cell(row=r, column=c).value for c in range(1, min(ws.max_column + 1, 8))])

    prompt = (
        f"Hoja activa: '{ws.title}', filas: {ws.max_row}, columnas: {ws.max_column}.\n"
        f"Muestra de filas: {muestra}\n"
        f"Instrucción del usuario: {instruction}\n"
        "Responde ÚNICAMENTE con un JSON válido (sin bloques ``` ni texto extra) con este formato:\n"
        '{"start_row": 2, "end_row": 10, "column": "E", "formula_template": "=C{row}*D{row}"}'
    )

    raw_reply = _invocar_agente(prompt)
    cleaned = (
        raw_reply.strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )

    try:
        plan = json.loads(cleaned)
        start_row = int(plan.get("start_row", 2))
        end_row = int(plan.get("end_row", ws.max_row))
        col_letter = str(plan.get("column", "E")).strip().upper()
        template = str(plan.get("formula_template", "")).strip()

        if not col_letter.isalpha():
            raise ValueError("La columna debe ser una letra válida (ej. E)")
        if not template.startswith("="):
            raise ValueError("La fórmula debe iniciar con '='")
        if start_row < 1 or end_row < start_row:
            raise ValueError("El rango de filas es inválido")

        for row in range(start_row, end_row + 1):
            ws[f"{col_letter}{row}"] = template.format(row=row)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"No se pudo aplicar la fórmula: {exc}")

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    safe_name = file.filename.replace('"', "")
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="formula_{safe_name}"'}
    )