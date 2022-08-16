from authentication.models import Notification
from forum.models import Tag, Comment


def get_db_tags(tags_titles: set[str]) -> tuple[Tag, ...]:
    """Returns tuple of Tag models.

    If tag with a certain title does not exist, then it is created.

    :param tags_titles: Set of tags' titles.
    :return: Tuple of Tag models.
    """
    tags_db = Tag.objects.filter(title__in=tags_titles)
    new_tags_db = []
    if len(tags_db) != len(tags_titles):
        existing_titles = {tag.title for tag in tags_db}
        new_titles = tags_titles - existing_titles
        new_tags_db.extend(Tag(title=title) for title in new_titles)
        new_tags_db = Tag.objects.bulk_create(new_tags_db)

    return *tags_db, *new_tags_db


def create_notification(comment: Comment) -> Notification:
    """Creates notification for a comment.

    :param comment: Comment instance.
    :return: Notification instance.
    """
    username = comment.author.username
    question_title = comment.question.title
    return Notification.objects.create(
        title=f'User {username} commented your question: "{question_title}".',
        user=comment.question.author,
        question=comment.question,
    )
