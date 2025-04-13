from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from io import BytesIO

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-trades")
async def upload_trades(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(BytesIO(contents))
    df['Lucro'] = (df['Venda'] - df['Compra']) * df['Quantidade'] - df['Corretagem']
    df['IR'] = df.apply(
        lambda row: 0 if row['Tipo'] == 'Ação' and row['TotalVendasMes'] <= 20000 else row['Lucro'] * (0.15 if row['TipoOperacao'] != 'DayTrade' else 0.20),
        axis=1
    )
    resumo = {
        "Lucro Total": round(df['Lucro'].sum(), 2),
        "Imposto Devido": round(df['IR'].sum(), 2)
    }
    return {"resumo": resumo, "detalhes": df.to_dict(orient='records')}

@app.post("/upload-dividendos")
async def upload_dividendos(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(BytesIO(contents))
    total = df['Valor'].sum()
    return {"total_dividendos": total, "dados": df.to_dict(orient='records')}

@app.post("/upload-alugueis")
async def upload_alugueis(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(BytesIO(contents))
    total = df['ValorBruto'].sum()
    return {"total_alugueis": total, "dados": df.to_dict(orient='records')}