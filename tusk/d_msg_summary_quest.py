def generate_summary(quest, xp_reward, gp_reward, honor_reward, honor_cost):
    return (
        f"**Quest Summary**\n"
        f"**Name:** {quest.quest_name}\n"
        f"**Challenge:** {quest.quest_real_goal}\n"
        f"**Mission:** {quest.quest_fict_goal}\n"
        f"**Intro:** {quest.quest_cutscene}\n"
        f"**Stage Descriptions:** {quest.quest_stage}\n"
        f"**Duration:** {quest.quest_duration_weeks} weeks\n"
        f"**Enemy:** {quest.quest_enemy}\n"
        f"**Difficulty:** {quest.quest_difficulty}\n"
        f"**XP Reward:** {xp_reward}\n"
        f"**GP Reward:** {gp_reward}\n"
        f"**Honor Reward:** {honor_reward}\n"
        f"**Honor Cost:** {honor_cost}\n"
    )
