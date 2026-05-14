<<<<<<< HEAD
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

from db.mongo import collection, users_collection
from models.knn_model import train_knn
from models.dt_model import train_dt

st.set_page_config(page_title="Smart Health", layout="wide")

# ---------------- AUTH ----------------

if "user" not in st.session_state:
    st.session_state.user = None


def auth_page():

    st.title("🔐 Smart Health App")

    choice = st.radio(
        "Select Option",
        ["Login", "Signup"]
    )

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    # ---------- SIGNUP ----------
    if choice == "Signup":

        if st.button("Create Account"):

            if users_collection.find_one(
                {"username": username}
            ):

                st.error("User already exists")

            else:

                users_collection.insert_one({
                    "username": username,
                    "password": password
                })

                st.success("Account created successfully")

    # ---------- LOGIN ----------
    if choice == "Login":

        if st.button("Login"):

            user = users_collection.find_one({
                "username": username,
                "password": password
            })

            if user:

                st.session_state.user = username
                st.rerun()

            else:

                st.error("Invalid username or password")


# stop if not logged in
if st.session_state.user is None:

    auth_page()
    st.stop()

# ---------------- LOAD DATA ----------------

all_data = pd.DataFrame(
    list(collection.find({}, {"_id": 0}))
)

# if empty DB
if len(all_data) == 0:

    st.warning("No records found in database.")
    st.stop()

# ---------- CLEAN COLUMNS ----------

all_data.columns = (
    all_data.columns
    .str.strip()
    .str.lower()
)

rename_map = {
    "sleep": "Sleep",
    "stress": "Stress",
    "activity": "Activity",
    "junkfood": "JunkFood",
    "water": "Water",
    "category": "Category",
    "user": "user",
    "time": "Time"
}

all_data.rename(
    columns=rename_map,
    inplace=True
)

# ---------- CREATE CATEGORY ----------

if "Category" not in all_data.columns:

    def assign_category(row):

        if (
            row["Sleep"] >= 7
            and row["Stress"] <= 4
            and row["Activity"] >= 6
        ):
            return "Good"

        elif (
            row["Stress"] >= 7
            or row["JunkFood"] >= 7
        ):
            return "Poor"

        else:
            return "Moderate"

    all_data["Category"] = all_data.apply(
        assign_category,
        axis=1
    )

# ---------- REMOVE NULLS ----------

all_data = all_data.dropna()

# ---------- USER DATA ----------

user_data = all_data[
    all_data["user"] == st.session_state.user
]

# ---------------- BALANCE DATASET ----------------

min_count = (
    all_data["Category"]
    .value_counts()
    .min()
)

categories = []

for cat in all_data["Category"].unique():

    temp = all_data[
        all_data["Category"] == cat
    ]

    temp = temp.sample(min_count)

    categories.append(temp)

balanced_data = pd.concat(categories)

balanced_data = (
    balanced_data
    .reset_index(drop=True)
)

# ---------------- TRAINING DATA ----------------

X = balanced_data[
    [
        'Sleep',
        'Stress',
        'Activity',
        'JunkFood',
        'Water'
    ]
]

y = balanced_data["Category"]

# ---------------- MODELS ----------------

knn, scaler = train_knn(X, y)

dt = train_dt(X, y)

# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.markdown(
        f"## 👋 {st.session_state.user}"
    )

    selected = option_menu(
        menu_title="Navigation",

        options=[
            "Home",
            "Predict",
            "Dashboard",
            "History",
            "To-Do"
        ],

        icons=[
            "house",
            "cpu",
            "bar-chart",
            "clock-history",
            "check2-square"
        ],

        default_index=0
    )

# ---------------- HOME ----------------

if selected == "Home":

    st.title("🌸 Smart Health Dashboard")

    if len(user_data) > 0:

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "🛌 Avg Sleep",
            round(
                user_data["Sleep"].mean(),
                1
            )
        )

        col2.metric(
            "😰 Avg Stress",
            round(
                user_data["Stress"].mean(),
                1
            )
        )

        col3.metric(
            "💧 Avg Water",
            round(
                user_data["Water"].mean(),
                1
            )
        )

    else:

        st.info(
            "No personal records found."
        )

# ---------------- PREDICT ----------------

elif selected == "Predict":

    st.title("🧠 Health Prediction")

    col1, col2 = st.columns(2)

    with col1:

        sleep = st.slider(
            "Sleep Hours",
            1,
            10,
            6
        )

        stress = st.slider(
            "Stress Level",
            1,
            10,
            5
        )

        activity = st.slider(
            "Activity Level",
            1,
            10,
            5
        )

    with col2:

        junk = st.slider(
            "Junk Food Intake",
            1,
            10,
            5
        )

        water = st.slider(
            "Water Intake",
            1,
            10,
            5
        )

    if st.button("Predict"):

        inp = [[
            sleep,
            stress,
            activity,
            junk,
            water
        ]]

        # ---------- SMART LOGIC ----------

        if (
            sleep >= 7
            and stress <= 4
            and activity >= 6
        ):

            k = "Good"

        elif (
            stress >= 7
            or junk >= 7
        ):

            k = "Poor"

        else:

            inp_scaled = scaler.transform(inp)

            k = knn.predict(
                inp_scaled
            )[0]

        d = dt.predict(inp)[0]

        # ---------- OUTPUT ----------

        st.success(
            f"KNN Prediction: {k}"
        )

        st.info(
            f"Decision Tree Prediction: {d}"
        )

        # ---------- FEEDBACK ----------

        if k == "Good":

            st.success(
                "✅ Excellent lifestyle."
            )

        elif k == "Moderate":

            st.warning(
                "⚠️ Moderate lifestyle."
            )

        else:

            st.error(
                "❌ Lifestyle needs improvement."
            )

        # ---------- SAVE ----------

        collection.insert_one({

            "user": st.session_state.user,

            "Sleep": sleep,

            "Stress": stress,

            "Activity": activity,

            "JunkFood": junk,

            "Water": water,

            "Category": k,

            "Time": pd.Timestamp.now()

        })

# ---------------- DASHBOARD ----------------

elif selected == "Dashboard":

    st.title("📊 Dashboard")

    if len(user_data) == 0:

        st.warning("No records found.")

    else:

        col1, col2 = st.columns(2)

        with col1:

            fig1 = px.pie(
                user_data,
                names="Category",
                title="Health Categories"
            )

            st.plotly_chart(
                fig1,
                use_container_width=True
            )

        with col2:

            avg = user_data[
                [
                    "Sleep",
                    "Stress",
                    "Activity",
                    "JunkFood",
                    "Water"
                ]
            ].mean().reset_index()

            avg.columns = [
                "Metric",
                "Value"
            ]

            fig2 = px.bar(
                avg,
                x="Metric",
                y="Value",
                title="Average Metrics"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

# ---------------- HISTORY ----------------

elif selected == "History":

    st.title("📜 User History")

    if len(user_data) == 0:

        st.info("No history available.")

    else:

        st.dataframe(
            user_data.sort_values(
                by="Time",
                ascending=False
            ),
            use_container_width=True
        )

# ---------------- TODO ----------------

elif selected == "To-Do":

    st.title("📝 Habit Tracker")

    if "tasks" not in st.session_state:

        st.session_state.tasks = []

    task = st.text_input(
        "Add New Habit"
    )

    if st.button("Add Habit"):

        if task.strip() != "":

            st.session_state.tasks.append(
                task
            )

    for i, t in enumerate(
        st.session_state.tasks
    ):

        col1, col2 = st.columns(
            [0.85, 0.15]
        )

        col1.write(f"✔ {t}")

        if col2.button(
            "Delete",
            key=i
        ):

            st.session_state.tasks.pop(i)

=======
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

from db.mongo import collection, users_collection
from models.knn_model import train_knn
from models.dt_model import train_dt

st.set_page_config(page_title="Smart Health", layout="wide")

# ---------------- AUTH ----------------

if "user" not in st.session_state:
    st.session_state.user = None


def auth_page():

    st.title("🔐 Smart Health App")

    choice = st.radio(
        "Select Option",
        ["Login", "Signup"]
    )

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    # ---------- SIGNUP ----------
    if choice == "Signup":

        if st.button("Create Account"):

            if users_collection.find_one(
                {"username": username}
            ):

                st.error("User already exists")

            else:

                users_collection.insert_one({
                    "username": username,
                    "password": password
                })

                st.success("Account created successfully")

    # ---------- LOGIN ----------
    if choice == "Login":

        if st.button("Login"):

            user = users_collection.find_one({
                "username": username,
                "password": password
            })

            if user:

                st.session_state.user = username
                st.rerun()

            else:

                st.error("Invalid username or password")


# stop if not logged in
if st.session_state.user is None:

    auth_page()
    st.stop()

# ---------------- LOAD DATA ----------------

all_data = pd.DataFrame(
    list(collection.find({}, {"_id": 0}))
)

# if empty DB
if len(all_data) == 0:

    st.warning("No records found in database.")
    st.stop()

# ---------- CLEAN COLUMNS ----------

all_data.columns = (
    all_data.columns
    .str.strip()
    .str.lower()
)

rename_map = {
    "sleep": "Sleep",
    "stress": "Stress",
    "activity": "Activity",
    "junkfood": "JunkFood",
    "water": "Water",
    "category": "Category",
    "user": "user",
    "time": "Time"
}

all_data.rename(
    columns=rename_map,
    inplace=True
)

# ---------- CREATE CATEGORY ----------

if "Category" not in all_data.columns:

    def assign_category(row):

        if (
            row["Sleep"] >= 7
            and row["Stress"] <= 4
            and row["Activity"] >= 6
        ):
            return "Good"

        elif (
            row["Stress"] >= 7
            or row["JunkFood"] >= 7
        ):
            return "Poor"

        else:
            return "Moderate"

    all_data["Category"] = all_data.apply(
        assign_category,
        axis=1
    )

# ---------- REMOVE NULLS ----------

all_data = all_data.dropna()

# ---------- USER DATA ----------

user_data = all_data[
    all_data["user"] == st.session_state.user
]

# ---------------- BALANCE DATASET ----------------

min_count = (
    all_data["Category"]
    .value_counts()
    .min()
)

categories = []

for cat in all_data["Category"].unique():

    temp = all_data[
        all_data["Category"] == cat
    ]

    temp = temp.sample(min_count)

    categories.append(temp)

balanced_data = pd.concat(categories)

balanced_data = (
    balanced_data
    .reset_index(drop=True)
)

# ---------------- TRAINING DATA ----------------

X = balanced_data[
    [
        'Sleep',
        'Stress',
        'Activity',
        'JunkFood',
        'Water'
    ]
]

y = balanced_data["Category"]

# ---------------- MODELS ----------------

knn, scaler = train_knn(X, y)

dt = train_dt(X, y)

# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.markdown(
        f"## 👋 {st.session_state.user}"
    )

    selected = option_menu(
        menu_title="Navigation",

        options=[
            "Home",
            "Predict",
            "Dashboard",
            "History",
            "To-Do"
        ],

        icons=[
            "house",
            "cpu",
            "bar-chart",
            "clock-history",
            "check2-square"
        ],

        default_index=0
    )

# ---------------- HOME ----------------

if selected == "Home":

    st.title("🌸 Smart Health Dashboard")

    if len(user_data) > 0:

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "🛌 Avg Sleep",
            round(
                user_data["Sleep"].mean(),
                1
            )
        )

        col2.metric(
            "😰 Avg Stress",
            round(
                user_data["Stress"].mean(),
                1
            )
        )

        col3.metric(
            "💧 Avg Water",
            round(
                user_data["Water"].mean(),
                1
            )
        )

    else:

        st.info(
            "No personal records found."
        )

# ---------------- PREDICT ----------------

elif selected == "Predict":

    st.title("🧠 Health Prediction")

    col1, col2 = st.columns(2)

    with col1:

        sleep = st.slider(
            "Sleep Hours",
            1,
            10,
            6
        )

        stress = st.slider(
            "Stress Level",
            1,
            10,
            5
        )

        activity = st.slider(
            "Activity Level",
            1,
            10,
            5
        )

    with col2:

        junk = st.slider(
            "Junk Food Intake",
            1,
            10,
            5
        )

        water = st.slider(
            "Water Intake",
            1,
            10,
            5
        )

    if st.button("Predict"):

        inp = [[
            sleep,
            stress,
            activity,
            junk,
            water
        ]]

        # ---------- SMART LOGIC ----------

        if (
            sleep >= 7
            and stress <= 4
            and activity >= 6
        ):

            k = "Good"

        elif (
            stress >= 7
            or junk >= 7
        ):

            k = "Poor"

        else:

            inp_scaled = scaler.transform(inp)

            k = knn.predict(
                inp_scaled
            )[0]

        d = dt.predict(inp)[0]

        # ---------- OUTPUT ----------

        st.success(
            f"KNN Prediction: {k}"
        )

        st.info(
            f"Decision Tree Prediction: {d}"
        )

        # ---------- FEEDBACK ----------

        if k == "Good":

            st.success(
                "✅ Excellent lifestyle."
            )

        elif k == "Moderate":

            st.warning(
                "⚠️ Moderate lifestyle."
            )

        else:

            st.error(
                "❌ Lifestyle needs improvement."
            )

        # ---------- SAVE ----------

        collection.insert_one({

            "user": st.session_state.user,

            "Sleep": sleep,

            "Stress": stress,

            "Activity": activity,

            "JunkFood": junk,

            "Water": water,

            "Category": k,

            "Time": pd.Timestamp.now()

        })

# ---------------- DASHBOARD ----------------

elif selected == "Dashboard":

    st.title("📊 Dashboard")

    if len(user_data) == 0:

        st.warning("No records found.")

    else:

        col1, col2 = st.columns(2)

        with col1:

            fig1 = px.pie(
                user_data,
                names="Category",
                title="Health Categories"
            )

            st.plotly_chart(
                fig1,
                use_container_width=True
            )

        with col2:

            avg = user_data[
                [
                    "Sleep",
                    "Stress",
                    "Activity",
                    "JunkFood",
                    "Water"
                ]
            ].mean().reset_index()

            avg.columns = [
                "Metric",
                "Value"
            ]

            fig2 = px.bar(
                avg,
                x="Metric",
                y="Value",
                title="Average Metrics"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

# ---------------- HISTORY ----------------

elif selected == "History":

    st.title("📜 User History")

    if len(user_data) == 0:

        st.info("No history available.")

    else:

        st.dataframe(
            user_data.sort_values(
                by="Time",
                ascending=False
            ),
            use_container_width=True
        )

# ---------------- TODO ----------------

elif selected == "To-Do":

    st.title("📝 Habit Tracker")

    if "tasks" not in st.session_state:

        st.session_state.tasks = []

    task = st.text_input(
        "Add New Habit"
    )

    if st.button("Add Habit"):

        if task.strip() != "":

            st.session_state.tasks.append(
                task
            )

    for i, t in enumerate(
        st.session_state.tasks
    ):

        col1, col2 = st.columns(
            [0.85, 0.15]
        )

        col1.write(f"✔ {t}")

        if col2.button(
            "Delete",
            key=i
        ):

            st.session_state.tasks.pop(i)

>>>>>>> 07cb0cbfc6be93d9be7f2b736ba6a03aa51ca954
            st.rerun()