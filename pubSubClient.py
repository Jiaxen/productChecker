from google.cloud import pubsub_v1
import logging

logger = logging.getLogger(__name__)


class PubSubClient:
    def __init__(self, project_id, topic_id):
        self.publisher = pubsub_v1.PublisherClient()
        # The `topic_path` method creates a fully qualified identifier
        # in the form `projects/{project_id}/topics/{topic_id}`
        self.topic_path = self.publisher.topic_path(project_id, topic_id)

    async def publish_to_topic(self, data):
        future = self.publisher.publish(self.topic_path, data.encode('utf-8'))
        logger.info(future.result())
