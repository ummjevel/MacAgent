"""Main entry point for MacAgent API server."""

import uvicorn
from macagent.core.config import settings


def main():
    """Run the FastAPI server."""
    uvicorn.run(
        "macagent.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
