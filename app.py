import streamlit as st
from workouts import WORKOUTS
workout_history=[]

def intensity_from_sleep(hours_slept):
    """
    Considers hours slept and turns into intensity 
    value for workout.
    """
    if hours_slept < 5:
        return ["low"]
    elif hours_slept <7:
        return ["low", "moderate"]
    elif hours_slept < 8:
        return ["moderate", "high"]
    else:
        return ["moderate", "high"]
    
def get_next_muscle_group(last_workout_muscle):
    """
    Determines which muscle groups to recommend based on last workout.
    Avoids working the same muscle group twice in a row.
    """
    if last_workout_muscle is None:
        return ["upper", "lower", "core", "full body"]
    # exclude last muscle worked
    all_groups = ["upper", "lower", "core", "full body"]
    available_groups = [group for group in all_groups if group != last_workout_muscle]
    
    return available_groups

def record_workout(workout):
    """
    Adds a completed workout to history.
    """
    workout_history.append({ # empty list at top, don't move
        "name": workout["name"],
        "muscle group": workout["muscle group"],
        "time": workout["time"],
        "intensity": workout["intensity"]
    })
    print(f"\n Workout recorded: {workout['name']}")

def recc_workout(free_time, muscle_group, free_equip, allowed_intensity, top_n=3):# for more/less options, modify n
    """
    Interates through all workouts and returns the top 3 
    closest to user's available time.

    free_time: amount of time the user has
    muscle_group: allowed muscle groups
    free_equip: list of available equipment
    allowed_intensity: allowed intensity levels from sleep
    top_n: how many workouts to return (default 3)
    """
    # setup equipment constraint
    equipment_access = {
        "open space": ["open space"],
        "mat": ["open space", "mat"],
        "track/trail": ["track/trail"],
        "gym": ["open space", "mat", "gym"]
    }
    # modify to suit multiselect
    available_equipment = []
    for eq in free_equip:
        available_equipment.extend(equipment_access.get(eq, []))
    available_equipment = list(set(available_equipment))

    # filter based on all criteria
    filtered_workouts = []
    for workout in WORKOUTS:
        if workout["time"] > free_time:
            continue
        if workout["muscle group"] not in muscle_group:
            continue
        if workout["equipment"] not in available_equipment:
            continue
        if workout["intensity"] not in allowed_intensity:
            continue
        filtered_workouts.append(workout)

    # use lambda to simply sort by closeness to free time
    filtered_workouts.sort(key=lambda w: abs(w["time"] - free_time))

    return filtered_workouts[:top_n]

def mark_workout_complete(workout_data):
    """Callback function to mark workout as complete."""
    st.session_state.workout_history.append({
        "name": workout_data["name"],
        "muscle group": workout_data["muscle group"],
        "time": workout_data["time"],
        "intensity": workout_data["intensity"]
    })
    st.session_state.just_completed = True

# STREAMLIT UI---------------------------------------------------------------------------------------
def main():
    # page setup 
    st.set_page_config( page_title="MoveIt - Think Less, Move More", 
                layout="centered" )
    
    # past workout check
    if 'just_completed' in st.session_state and st.session_state.just_completed:
        st.session_state.just_completed = False
        st.rerun()
    
    # title
    st.title(
    "MoveIt - Think Less, Move More"
    )
    st.markdown(
    "Get a personalized workout recommendations based on your time, equipment, and energy level."
    )    
    st.divider()
    
    # initalize session state for workout history
    if 'workout_history' not in st.session_state:
        st.session_state.workout_history = []
    if len(st.session_state.workout_history) == 0:
        st.header("First Time Setup")
        
        had_previous = st.radio(
            "Did you work out recently?",
            options=["No", "Yes"],
            index=0
        )
        
        if had_previous == "Yes":
            last_muscle = st.selectbox(
                "What muscle group did you work last?",
                options=["upper", "lower", "core", "full body"]
            )
            
            if st.button("Save Previous Workout Info"):
                st.session_state.workout_history.append({
                    "name": "Previous Workout",
                    "muscle group": last_muscle,
                    "time": 0,
                    "intensity": "unknown"
                })
                st.success(f"Saved! We'll avoid {last_muscle} workouts today.")
                st.rerun()
        
        st.divider()
    
    # show last workout if exists
    if len(st.session_state.workout_history) > 0:
        last = st.session_state.workout_history[-1]
        st.info(f"Last workout: {last['name']} ({last['muscle group']})")
    
    # current workout recc
    st.header("Your Next Workout")
    col1, col2 = st.columns(2)
    with col1:
        free_time = st.number_input(
        "Time Available (90 min max)?",
        min_value=5,
        max_value=90,
        value=30,
        step=1)
    
    with col2:
        hours_slept = st.number_input(
        "Hours of Sleep?",
        min_value=1,
        max_value=15,
        value=8,
        step=1)
    
    st.markdown("Available Equipment (select all that apply)?")
    equipment_options = ["open space", "mat", "track/trail", "gym"]
    cols = st.columns(len(equipment_options))
    free_equip = []

    for i, option in enumerate(equipment_options):
        with cols[i]:
            checked = st.checkbox(option.title())
            if checked:
                free_equip.append(option)

    st.divider()
    
    # recc button
    if st.button("Get Workout Recommendations", type="primary", use_container_width=True):
        # determine allowed muscle groups
        last_muscle = st.session_state.workout_history[-1]["muscle group"] if st.session_state.workout_history else None
        allowed_muscle_groups = get_next_muscle_group(last_muscle)
        
        # get intensity from sleep input
        allowed_intensity = intensity_from_sleep(hours_slept)
        
        # get recommendations
        recommendations = recc_workout(free_time, allowed_muscle_groups, free_equip, allowed_intensity)
        
        # display
        if recommendations:
            st.success(f"Found {len(recommendations)} workout(s) for you!")
            st.subheader("Your Recommended Workouts:")
            
            for i, workout in enumerate(recommendations, 1):
                with st.expander(f"Option {i}: {workout['name']}", expanded=(i==1)):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Duration", f"{workout['time']} min")
                    with col2:
                        st.metric("Intensity", workout['intensity'].title())
                    with col3:
                        st.metric("Type", workout['type'].title())
                    with col4:
                        st.metric("Muscle", workout['muscle group'].title())
                    
                    st.markdown(f"**Equipment:** {workout['equipment'].title()}")
                    
                    # complete button
                    st.button(
                        f"I completed this workout", 
                        key=f"complete_{i}",
                        on_click=mark_workout_complete,
                        args=(workout,)
                    )
        else:
            st.error("No workouts found - adjust your time or equipment.")
    
    # SIDEBAR: Workout History
    with st.sidebar:
        st.header("Workout History")
        
        if st.session_state.workout_history:
            for i, w in enumerate(st.session_state.workout_history, 1):
                if w['name'] != "Previous Workout":
                    st.write(f"{i}. **{w['name']}**")
                    st.caption(f"{w['muscle group']} • {w['time']}min • {w['intensity']}")
        else:
            st.write("No workouts recorded yet!")
        
        # clear history button
        if st.session_state.workout_history and st.button("Clear History"):
            st.session_state.workout_history = []
            st.rerun()


if __name__ == "__main__":
    main()
