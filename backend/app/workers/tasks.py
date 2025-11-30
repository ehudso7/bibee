"""Celery background tasks."""
from app.workers.celery_app import celery_app
from app.pipelines.stem_separation import separate_stems
from app.pipelines.mixing import mix_tracks


@celery_app.task(bind=True)
def process_stems_task(self, input_path: str, output_dir: str, project_id: str):
    """Background task for stem separation."""
    def progress_callback(progress, message):
        self.update_state(state="PROGRESS", meta={"progress": progress, "message": message})

    stems = separate_stems(input_path, output_dir, progress_callback=progress_callback)
    return {"project_id": project_id, "stems": stems}


@celery_app.task(bind=True)
def mix_project_task(self, instrumental_path: str, vocal_path: str, output_path: str, settings: dict):
    """Background task for mixing."""
    def progress_callback(progress, message):
        self.update_state(state="PROGRESS", meta={"progress": progress, "message": message})

    result = mix_tracks(
        instrumental_path,
        vocal_path,
        output_path,
        vocal_level=settings.get("vocal_level", 0.0),
        reverb_amount=settings.get("reverb_amount", 0.2),
        progress_callback=progress_callback,
    )
    return {"output_path": result}
