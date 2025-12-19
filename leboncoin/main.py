import json
import os
import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

data_batch = []
BATCH_SIZE = 100
CSV_FILE = "donnees.csv"
BACKUP_FILE = "backup_donnees.json"
COLUMNS = ["tel", "siret", "description", "website"]

total = 1

def backup_failed_data(batch, reason="Erreur inconnue"):

    #backup data informations and the rason 
    try:
        backup_data = {
            "reason": reason,
            "data": batch
        }
         
        if os.path.exists(BACKUP_FILE):
            with open(BACKUP_FILE, "r", encoding="utf-8") as f:
                old = json.load(f)
                if isinstance(old, list):
                    old.append(backup_data)
                else:
                    old = [backup_data]
        else:
            old = [backup_data]

        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(old, f, indent=2, ensure_ascii=False)

        print(f"🆘 Données sauvegardées dans {BACKUP_FILE} en cas d'erreur.")

    except Exception as e:
        print("🚨 Impossible de sauvegarder dans le fichier de secours :", e)


def save_batch_to_csv(batch):
    try:
        # Charger les anciennes données si fichier existe
        if os.path.exists(CSV_FILE):
            df_existing = pd.read_csv(CSV_FILE, dtype=str)
        else:
            df_existing = pd.DataFrame(columns=COLUMNS)

        df_new = pd.DataFrame(batch)

        for col in COLUMNS:
            if col not in df_new.columns:
                df_new[col] = None
            if col not in df_existing.columns:
                df_existing[col] = None

        df_new = df_new[COLUMNS]
        df_existing = df_existing[COLUMNS]

        df_merged = pd.concat([df_existing, df_new], ignore_index=True)

        df_merged.to_csv(CSV_FILE, mode='w', header=True, index=False, encoding="utf-8")
        print(f"✅ {len(df_new)} nouvelles lignes ajoutées. Total : {len(df_merged)}")

    except Exception as e:
        print("❌ Erreur pendant la sauvegarde CSV :", e)
        backup_failed_data(batch, str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global data_batch
    global total

    await websocket.accept()
    try:
        while True:
            data_text = await websocket.receive_text()
            data = json.loads(data_text)
            print("📥 Reçu :", data, "| Total :", total)
            total += 1

            data_batch.append(data)

            if len(data_batch) >= BATCH_SIZE:
                save_batch_to_csv(data_batch)
                data_batch = []

            await websocket.send_text("✅ Message reçu")

    except WebSocketDisconnect:
        print("⚠️ Client déconnecté proprement.")
    except Exception as e:
        print("❌ Erreur WebSocket :", e)
    finally:
        if data_batch:
            print("📦 Sauvegarde des données restantes en mémoire...")
            save_batch_to_csv(data_batch)
            data_batch = []
