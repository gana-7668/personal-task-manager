import json
import os
from datetime import datetime, timedelta
import streamlit as st

# Constants
DATA_FILE = "tasks.json"
DATE_FORMAT = "%Y-%m-%d"

# Initialize session state for tasks if not already present
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# Load tasks from file at startup
def load_tasks():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

# Save tasks to file
def save_tasks(tasks):
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

# Initialize tasks in session state on first run
if len(st.session_state.tasks) == 0:
    st.session_state.tasks = load_tasks()

# Categories and priorities
CATEGORIES = ["Work", "Personal", "Study", "Health", "Other"]
PRIORITIES = ["High", "Medium", "Low"]

# Helper: Reassign task IDs after deletion
def reassign_ids(tasks):
    for i, task in enumerate(tasks, 1):
        task["id"] = i
    return tasks

# Helper: Get task by ID
def get_task_by_id(task_id):
    return next((t for t in st.session_state.tasks if t["id"] == task_id), None)

# Page config
st.set_page_config(page_title="Personal Task Manager", layout="wide")
st.title("📝 Personal Task Manager")

# Sidebar Navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", [
    "View All Tasks",
    "Add New Task",
    "Update Task",
    "Delete Task",
    "Filter by Category",
    "Filter by Priority",
    "Upcoming Tasks",
    "Mark as Complete",
    "Statistics"
])

# --- PAGE: View All Tasks ---
if page == "View All Tasks":
    st.header("📋 All Tasks")
    if not st.session_state.tasks:
        st.info("No tasks found. Add a new task to get started!")
    else:
        for task in st.session_state.tasks:
            status = "✅ Completed" if task["completed"] else "❌ Incomplete"
            due_date = task["due_date"] if task["due_date"] else "No due date"
            with st.expander(f"{task['title']} (ID: {task['id']}) - {status}"):
                st.write(f"**Description:** {task['description']}")
                st.write(f"**Category:** {task['category']}")
                st.write(f"**Priority:** {task['priority']}")
                st.write(f"**Due Date:** {due_date}")
                st.write(f"**Created At:** {task['created_at']}")

# --- PAGE: Add New Task ---
elif page == "Add New Task":
    st.header("➕ Add New Task")

    title = st.text_input("Task Title *", help="Required field")
    description = st.text_area("Description", value="")

    category = st.selectbox("Category", CATEGORIES, index=4)  # Default: Other
    priority = st.selectbox("Priority", PRIORITIES, index=1)  # Default: Medium

    due_date = st.date_input("Due Date (Optional)", value=None)
    due_date_str = due_date.strftime(DATE_FORMAT) if due_date else None

    if st.button("Add Task"):
        if not title.strip():
            st.error("Title cannot be empty!")
        else:
            new_task = {
                "id": len(st.session_state.tasks) + 1,
                "title": title.strip(),
                "description": description.strip(),
                "category": category,
                "priority": priority,
                "due_date": due_date_str,
                "completed": False,
                "created_at": datetime.now().strftime(DATE_FORMAT)
            }
            st.session_state.tasks.append(new_task)
            save_tasks(st.session_state.tasks)
            st.success(f"Task '{title}' added successfully!")

# --- PAGE: Update Task ---
elif page == "Update Task":
    st.header("✏️ Update Task")

    if not st.session_state.tasks:
        st.warning("No tasks available to update.")
    else:
        task_ids = [task["id"] for task in st.session_state.tasks]
        selected_id = st.selectbox("Select Task ID to Update", task_ids)

        task = get_task_by_id(selected_id)
        if task:
            st.subheader(f"Updating: {task['title']}")

            new_title = st.text_input("Title", value=task["title"])
            new_description = st.text_area("Description", value=task["description"])

            new_category = st.selectbox(
                "Category",
                CATEGORIES,
                index=CATEGORIES.index(task["category"])
            )
            new_priority = st.selectbox(
                "Priority",
                PRIORITIES,
                index=PRIORITIES.index(task["priority"])
            )

            current_due = datetime.strptime(task["due_date"], DATE_FORMAT) if task["due_date"] else None
            new_due_date = st.date_input("Due Date", value=current_due)
            new_due_date_str = new_due_date.strftime(DATE_FORMAT) if new_due_date else None

            if st.button("Update Task"):
                task["title"] = new_title.strip() if new_title.strip() else task["title"]
                task["description"] = new_description.strip()
                task["category"] = new_category
                task["priority"] = new_priority
                task["due_date"] = new_due_date_str

                save_tasks(st.session_state.tasks)
                st.success("Task updated successfully!")

# --- PAGE: Delete Task ---
elif page == "Delete Task":
    st.header("🗑️ Delete Task")

    if not st.session_state.tasks:
        st.warning("No tasks to delete.")
    else:
        task_ids_titles = {task["id"]: task["title"] for task in st.session_state.tasks}
        selected_id = st.selectbox(
            "Select Task to Delete",
            options=list(task_ids_titles.keys()),
            format_func=lambda x: f"{x}: {task_ids_titles[x]}"
        )

        if st.button("Delete Task"):
            confirm = st.checkbox(f"Confirm deletion of '{task_ids_titles[selected_id]}'")
            if confirm:
                st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != selected_id]
                st.session_state.tasks = reassign_ids(st.session_state.tasks)
                save_tasks(st.session_state.tasks)
                st.success("Task deleted successfully!")
            else:
                st.info("Please confirm deletion.")

# --- PAGE: Filter by Category ---
elif page == "Filter by Category":
    st.header("📂 Filter by Category")
    selected_category = st.selectbox("Choose Category", CATEGORIES)
    filtered = [t for t in st.session_state.tasks if t["category"] == selected_category]

    if filtered:
        for task in filtered:
            status = "✅" if task["completed"] else "❌"
            st.write(f"{status} **{task['title']}** (ID: {task['id']}) — Due: {task.get('due_date', 'N/A')}")
    else:
        st.info(f"No tasks found in category: {selected_category}")

# --- PAGE: Filter by Priority ---
elif page == "Filter by Priority":
    st.header("⚠️ Filter by Priority")
    selected_priority = st.selectbox("Choose Priority", PRIORITIES)
    filtered = [t for t in st.session_state.tasks if t["priority"] == selected_priority]

    if filtered:
        for task in filtered:
            status = "✅" if task["completed"] else "❌"
            st.write(f"{status} **{task['title']}** (ID: {task['id']}) — Category: {task['category']}")
    else:
        st.info(f"No tasks found with priority: {selected_priority}")

# --- PAGE: Upcoming Tasks ---
elif page == "Upcoming Tasks":
    st.header("⏳ Upcoming Tasks (Next 7 Days)")
    today = datetime.now()
    upcoming = []

    for task in st.session_state.tasks:
        if task["due_date"] and not task["completed"]:
            due_dt = datetime.strptime(task["due_date"], DATE_FORMAT)
            if today <= due_dt <= today + timedelta(days=7):
                upcoming.append(task)

    if upcoming:
        for task in upcoming:
            st.warning(f"**{task['title']}** — Due: {task['due_date']} (Category: {task['category']})")
    else:
        st.info("No upcoming tasks in the next 7 days.")

# --- PAGE: Mark as Complete ---
elif page == "Mark as Complete":
    st.header("✅ Mark Task as Complete")
    incomplete = [t for t in st.session_state.tasks if not t["completed"]]

    if not incomplete:
        st.info("All tasks are already completed!")
    else:
        task_options = {t["id"]: t["title"] for t in incomplete}
        selected_id = st.selectbox(
            "Select Task to Mark Complete",
            options=list(task_options.keys()),
            format_func=lambda x: f"{x}: {task_options[x]}"
        )

        if st.button("Mark as Complete"):
            task = get_task_by_id(selected_id)
            if task:
                task["completed"] = True
                save_tasks(st.session_state.tasks)
                st.success(f"Task '{task['title']}' marked as complete!")

# --- PAGE: Statistics ---
elif page == "Statistics":
    st.header("📊 Task Statistics")

    total = len(st.session_state.tasks)
    completed = len([t for t in st.session_state.tasks if t["completed"]])
    incomplete = total - completed

    st.metric("Total Tasks", total)
    st.metric("Completed Tasks", completed)
    st.metric("Incomplete Tasks", incomplete)

    if total > 0:
        rate = (completed / total) * 100
        st.progress(rate / 100, text=f"Completion Rate: {rate:.1f}%")

    # Category stats
    st.subheader("By Category")
    cat_data = {cat: len([t for t in st.session_state.tasks if t["category"] == cat]) for cat in CATEGORIES}
    st.bar_chart(cat_data)

    # Priority stats
    st.subheader("By Priority")
    pri_data = {pri: len([t for t in st.session_state.tasks if t["priority"] == pri]) for pri in PRIORITIES}
    st.bar_chart(pri_data)

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Data is saved automatically to `tasks.json`")