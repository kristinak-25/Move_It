# MoveIt - Workout Decision Tool
### Overview
MoveIt is a tool that reccomends your daily workout. It is ideal for anyone whose barrier to movement is deciding what they will do that day to move their body. It is for anyone who dislikes the predicatabiltiy of a workout split, wants to move each day, and has holistic workout goals like increasing strength, endurance, and mobility. MoveIt steamlines decision making so you can think less and move more. 
### Problem Statement
Starting a workout is hard when you have no plan. MoveIt automates your workout decision by filtering predefined workouts based on daily constraints 
like time, equipment, and recently trained muscle groups.
### How it Works
1. Workouts are defined as structured data (muscle group, duration, equipment, intensity, workout type)
2. User state is collected prior to workout (available time, equipment, recent muscle groups, )
3. Rules functions translate user state into constraints (allowed intensity, muscles to avoid)
4. Workouts are filtered based on constraints
5. One workout is selected and returned, optinally workout is stored
