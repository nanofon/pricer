import asyncio
from pipeline.service import service_loop

if __name__ == "__main__":
    try:
        asyncio.run(service_loop())
    except KeyboardInterrupt:
        print("Crawler stopped.")
