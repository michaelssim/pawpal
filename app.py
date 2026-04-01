import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

PRIORITY_EMOJI = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# --- Section 1: Owner & Pet Setup ---
st.subheader("Owner & Pet Setup")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input("Time available today (minutes)", min_value=10, max_value=480, value=60)
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Save profile"):
    owner = Owner(owner_name, int(available_minutes))
    pet = Pet(pet_name, species, age=0)
    owner.add_pet(pet)               # Owner.add_pet() links the pet to this owner
    st.session_state.owner = owner   # store the whole owner (with pet inside) in the vault
    st.success(f"Profile saved! Owner: {owner.name} | Pet: {pet.name} ({pet.species})")

if "owner" in st.session_state:
    st.caption("Current pets:")
    for pet in st.session_state.owner.get_pets():   # Owner.get_pets() reads from the vault
        st.markdown(f"- **{pet.name}** ({pet.species})")

st.divider()

# --- Section 2: Add Tasks ---
st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    if "owner" not in st.session_state:
        st.warning("Save your profile first before adding tasks.")
    else:
        pet = st.session_state.owner.get_pets()[0]
        pet.add_task(Task(task_title, int(duration), priority, "general"))  # Pet.add_task() wires directly to the object
        st.success(f"Added '{task_title}' to {pet.name}'s task list.")

if "owner" in st.session_state:
    scheduler = Scheduler(st.session_state.owner)
    sorted_tasks = scheduler._sort_tasks()  # display tasks in scheduled priority order
    if sorted_tasks:
        st.write("Current tasks (sorted by priority):")
        st.dataframe(
            [{"title": t.title, "duration (min)": t.duration_minutes, "priority": PRIORITY_EMOJI.get(t.priority, t.priority), "completed": t.completed}
             for t in sorted_tasks],
            use_container_width=True,
        )
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            for warning in conflicts:
                st.warning(warning)
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Section 3: Build Schedule ---
st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

col_generate, col_reset = st.columns([3, 1])

with col_generate:
    generate_clicked = st.button("Generate schedule")
with col_reset:
    if st.button("Reset") and "owner" in st.session_state:
        del st.session_state.owner
        st.rerun()

if generate_clicked:
    if "owner" not in st.session_state:
        st.warning("Save your profile first.")
    elif not st.session_state.owner.get_pets()[0].get_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        plan = Scheduler(st.session_state.owner).generate_plan()  # Scheduler reads directly from the vault
        pet = st.session_state.owner.get_pets()[0]

        st.success(f"Plan generated for {pet.name}! Total time: {plan.total_duration} min / {st.session_state.owner.get_available_minutes()} min available.")

        if plan.scheduled_tasks:
            st.markdown("### Scheduled")
            st.table([
                {"title": t.title, "duration (min)": t.duration_minutes, "priority": PRIORITY_EMOJI.get(t.priority, t.priority)}
                for t in plan.scheduled_tasks
            ])

        if plan.skipped_tasks:
            st.markdown("### Skipped (not enough time)")
            st.table([
                {"title": t.title, "duration (min)": t.duration_minutes, "priority": PRIORITY_EMOJI.get(t.priority, t.priority)}
                for t in plan.skipped_tasks
            ])

        with st.expander("Why was this plan chosen?"):
            st.text(plan.explain())

    st.markdown(
        """
Suggested approach:
1. Design your UML (draft).
2. Create class stubs (no logic).
3. Implement scheduling behavior.
4. Connect your scheduler here and display results.
"""
    )
