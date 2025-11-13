# FlowMind Core API

FlowMind, kullanıcıların teknik bilgiye ihtiyaç duymadan kendi yapay zeka otomasyon akışlarını oluşturabildiği bir platformdur.  
Bu repo, FlowMind'in **çekirdek backend API** katmanıdır ve **FastAPI** + **SQLite** üzerinde çalışır. Uygulama Hugging Face Spaces üzerinde host edilecektir.

## Özellikler (Planlanan)

- 🌐 REST API (FastAPI)
- 🧠 Yapay zeka destekli workflow tasarımı (AI Assistant)
- 🧩 Workflow, Node ve Edge modelleri (no-code otomasyon)
- 🗄️ SQLite tabanlı kalıcı veritabanı (HF Space içinde `data/app.db`)
- 📜 Çalıştırma logları (workflow_runs, workflow_step_logs)
- 🔑 Kullanıcı bazlı LLM API anahtarı yönetimi (BYOK)
- 🧪 Dry-run ve debug desteği

## Teknoloji Stack

- Python 3.10+
- FastAPI
- SQLAlchemy
- SQLite (HF filesystem içinde)
- Hugging Face Spaces (FastAPI Space)

## Mimarideki Rolü

Bu servis:

- Frontend (FlowMind Web UI) ile HTTP üzerinden konuşur.
- Workflow CRUD, çalıştırma (execution) ve loglama işlerini yapar.
- AI Assistant için gerekli backend endpoint’lerini sağlar.
- Env değişkenler, API anahtarları ve cron tetikleyici (scheduler) ile tüm otomasyon motorunu yönetir.

---

Bu README ilk taslaktır ve proje ilerledikçe güncellenecektir.
