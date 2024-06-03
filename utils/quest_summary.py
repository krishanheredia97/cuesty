from firebase_admin import db


def generate_summary(quest_id):
    """
    Generate a summary of the quest configuration in markdown format.

    :param quest_id: The ID of the quest.
    :return: The summary in markdown format.
    """
    ref = db.reference(f'quests/{quest_id}')
    quest_data = ref.get()

    if not quest_data:
        return "Quest not found."

    summary = "# Quest Summary\n"
    for category, items in quest_data.items():
        summary += f"## {category}\n"
        for item, value in items.items():
            if value is not None:
                summary += f"- **{item}**: {value}\n"

    return summary
