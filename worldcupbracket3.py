import streamlit as st

st.set_page_config(page_title="2026 World Cup Bracket Predictor Created By Abhi Nandi", layout="wide")

GROUP_TEAMS = {
    "A": ["Mexico", "South Africa", "South Korea", "Czechia"],
    "B": ["Canada", "Qatar", "Switzerland", "Bosnia and Herzegovina"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "Türkiye"],
    "E": ["Germany", "Curaçao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

ROUND32 = [
    ("M73", "2A", "2B"),
    ("M74", "1E", "3?"),
    ("M75", "1F", "2C"),
    ("M76", "1C", "2F"),
    ("M77", "1I", "3?"),
    ("M78", "2E", "2I"),
    ("M79", "1A", "3?"),
    ("M80", "1L", "3?"),
    ("M81", "1D", "3?"),
    ("M82", "1G", "3?"),
    ("M83", "2K", "2L"),
    ("M84", "1H", "2J"),
    ("M85", "1B", "3?"),
    ("M86", "1J", "2H"),
    ("M87", "1K", "3?"),
    ("M88", "2D", "2G"),
]

THIRD_SLOTS = {
    "M74": list("ABCDF"),
    "M77": list("CDFGH"),
    "M79": list("CEFHI"),
    "M80": list("EHIJK"),
    "M81": list("BEFIJ"),
    "M82": list("AEHIJ"),
    "M85": list("EFGIJ"),
    "M87": list("DEIJL"),
}

NEXT_ROUNDS = {
    "Round of 16": [
        ("M89", "W73", "W75"),
        ("M90", "W74", "W77"),
        ("M91", "W76", "W78"),
        ("M92", "W79", "W80"),
        ("M93", "W83", "W84"),
        ("M94", "W81", "W82"),
        ("M95", "W86", "W88"),
        ("M96", "W85", "W87"),
    ],
    "Quarterfinals": [
        ("M97", "W89", "W90"),
        ("M98", "W93", "W94"),
        ("M99", "W91", "W92"),
        ("M100", "W95", "W96"),
    ],
    "Semifinals": [
        ("M101", "W97", "W98"),
        ("M102", "W99", "W100"),
    ],
    "Final": [
        ("M104", "W101", "W102"),
    ],
}


def assign_third_place_groups(selected_groups):
    slots = list(THIRD_SLOTS.keys())

    def backtrack(index, used, assignment):
        if index == len(slots):
            return assignment

        slot = slots[index]

        for group in selected_groups:
            if group not in used and group in THIRD_SLOTS[slot]:
                result = backtrack(
                    index + 1,
                    used | {group},
                    {**assignment, slot: f"3{group}"},
                )
                if result:
                    return result

        return None

    return backtrack(0, set(), {})


def label_to_team(label, teams):
    place = label[0]
    group = label[1]
    return teams[group][place]


def get_team(label, teams, winners):
    if label.startswith("W"):
        return winners.get(label[1:], label)

    return label_to_team(label, teams)


def play_round(round_name, fixtures, teams, winners):
    st.subheader(round_name)

    cols = st.columns(2)

    for i, (match_id, a, b) in enumerate(fixtures):
        team_a = get_team(a, teams, winners)
        team_b = get_team(b, teams, winners)

        with cols[i % 2]:
            winner = st.radio(
                f"{match_id}: {team_a} vs {team_b}",
                [team_a, team_b],
                key=match_id,
                horizontal=True,
            )

        winners[match_id[1:]] = winner


def draw_bracket_graph(round32, winners, teams):
    lines = [
        "digraph G {",
        "rankdir=LR;",
        "graph [pad=0.2, nodesep=0.35, ranksep=0.55];",
        "node [shape=box, style=rounded, fontsize=9];",
        "edge [arrowsize=0.6];",
    ]

    all_rounds = {
        "Round of 32": round32,
        **NEXT_ROUNDS,
    }

    for round_name, fixtures in all_rounds.items():
        for match_id, a, b in fixtures:
            team_a = get_team(a, teams, winners)
            team_b = get_team(b, teams, winners)
            winner = winners.get(match_id[1:], "")

            label = f"{match_id}\\n{team_a}\\nvs\\n{team_b}"

            if winner:
                label += f"\\nWinner: {winner}"

            lines.append(f'"{match_id}" [label="{label}"];')

            if a.startswith("W"):
                lines.append(f'"M{a[1:]}" -> "{match_id}";')

            if b.startswith("W"):
                lines.append(f'"M{b[1:]}" -> "{match_id}";')

    champion = winners.get("104")

    if champion:
        lines.append(f'"Champion" [label="Champion\\n{champion}", shape=doubleoctagon];')
        lines.append('"M104" -> "Champion";')

    lines.append("}")

    return "\n".join(lines)


st.title("2026 World Cup Bracket Predictor Created By Abhi Nandi")

st.write(
    "Pick the winner, runner-up, and third-place team from each group. "
    "Then select the 8 best third-place teams and play through the bracket."
)

main_col, bracket_col = st.columns([2, 1])

with main_col:
    teams = {}

    st.header("Group Stage Picks")

    for group, group_teams in GROUP_TEAMS.items():
        with st.expander(f"Group {group}", expanded=False):
            winner = st.selectbox(
                f"Group {group} Winner",
                group_teams,
                key=f"winner_{group}",
            )

            runner_options = [team for team in group_teams if team != winner]

            runner = st.selectbox(
                f"Group {group} Runner-up",
                runner_options,
                key=f"runner_{group}",
            )

            third_options = [
                team for team in group_teams
                if team not in [winner, runner]
            ]

            third = st.selectbox(
                f"Group {group} Third Place",
                third_options,
                key=f"third_{group}",
            )

            teams[group] = {
                "1": winner,
                "2": runner,
                "3": third,
            }

    st.header("Best Third-Place Teams")

    third_place_options = {
        f"Group {group}: {teams[group]['3']}": group
        for group in GROUP_TEAMS
    }

    selected_third_labels = st.multiselect(
        "Select exactly 8 third-place teams",
        list(third_place_options.keys()),
        max_selections=8,
    )

    selected_third_groups = [
        third_place_options[label]
        for label in selected_third_labels
    ]

    winners = {}
    round32 = []

    bracket_ready = False

    if len(selected_third_groups) == 8:
        third_assignment = assign_third_place_groups(selected_third_groups)

        if third_assignment:
            bracket_ready = True
            st.success("Bracket generated.")

            for match_id, team_a, team_b in ROUND32:
                if team_b == "3?":
                    team_b = third_assignment[match_id]

                round32.append((match_id, team_a, team_b))

            play_round("Round of 32", round32, teams, winners)

            for round_name, fixtures in NEXT_ROUNDS.items():
                play_round(round_name, fixtures, teams, winners)

            st.header("Champion")

            champion = winners.get("104")

            if champion:
                st.success(f"🏆 Champion: {champion}")
        else:
            st.error("This third-place combination could not be assigned to the bracket.")
    else:
        st.info("Select exactly 8 third-place teams to generate the bracket.")

with bracket_col:
    st.subheader("Live Bracket Preview")

    if bracket_ready:
        st.graphviz_chart(draw_bracket_graph(round32, winners, teams))
    else:
        st.info("The bracket preview will appear here after you select 8 third-place teams.")

