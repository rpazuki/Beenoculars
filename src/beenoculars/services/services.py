import logging
from typing import Any

import beenoculars.core as core
from beenoculars.image_processing.pipelines import ImageProcessingPipeline

log = logging.getLogger(__name__)


class GeneraicAlgorithm(core.SyncServiceStrategy):
    def __init__(self,
                 pipline: ImageProcessingPipeline,
                 callback=None,
                 **kwargs):
        super().__init__()
        self.pipeline = pipline
        self.callback = callback
        self.kwargs = kwargs

    @core.safe_call(log)
    def handle_event(self, widget: Any, app: core.AbstractApp, *args, **kwargs):
        frame = app.original_image
        if self.callback is not None:
            key_values_args = self.kwargs | self.callback()
        else:
            key_values_args = self.kwargs
        image = self.pipeline.process(frame, **key_values_args)
        app.layout.image_view.image = image
