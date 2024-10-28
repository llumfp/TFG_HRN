(define (domain domain_goals)

(:requirements :durative-actions :negative-preconditions :action-costs :adl)
(:types agent loc action tool goal - object
    dynamic_action static_action static_action_tool dynamic_action_tool - action
)
 
(:predicates
    (agent_not_busy ?agent - agent)
    (holding ?agent - agent ?tool - tool)
    (handfree ?agent - agent)

    (toolfree ?tool - tool)

    (is_at ?obj - object ?loc - loc)
    (action_executed ?action - action ?agent - agent)
     
    (action_loc ?action - action ?loc - loc)
    (action_end_loc ?action - action ?loc - loc)
    (action_tool ?action - action ?tool - tool)

    (goal_action ?goal - goal ?action - action)
    (goal_pending ?goal - goal)
    (goal_finished ?goal - goal)
    (goal_executed ?goal - goal ?agent - agent)
)

(:functions
    ; each action has an associated cost
    (action_cost ?agent - agent ?action - action)
    (total-cost ?agent - agent)
)

(:durative-action execute_action
 :parameters (?action - static_action ?agent - agent ?loc - loc)
 :duration (= ?duration 10)
 :condition (and
    (at start (agent_not_busy ?agent))
    (at start (is_at ?agent ?loc))
    (at start (action_loc ?action ?loc))
    (at start (handfree ?agent))
    )

 :effect (and
    (at start (not (handfree ?agent)))
    (at start (not (agent_not_busy ?agent)))
    (at end (agent_not_busy ?agent))
    (at end (handfree ?agent))
    (at end (action_executed ?action ?agent))
    (at start (increase (total-cost ?agent) (action_cost ?agent ?action)))
    )
)

(:durative-action move_to_loc
 :parameters (?agent - agent ?init_loc - loc ?end_loc - loc)
 :duration (= ?duration 10)
 :condition (and
    (at start (agent_not_busy ?agent))
    (at start (is_at ?agent ?init_loc))
    (at start (handfree ?agent))
 )
 :effect (and
    (at end (is_at ?agent ?end_loc))
    (at start (not (is_at ?agent ?init_loc)))
    (at start (not (agent_not_busy ?agent)))
    (at end (agent_not_busy ?agent))
    )
)

(:durative-action move_to_loc_with_tool
 :parameters (?agent - agent ?init_loc - loc ?end_loc - loc ?tool - tool)
 :duration (= ?duration 10)
 :condition (and
    (at start (agent_not_busy ?agent))
    (at start (is_at ?agent ?init_loc))
    (at start (is_at ?tool ?init_loc))
    (at start (holding ?agent ?tool))
 )
 :effect (and
    (at end (is_at ?agent ?end_loc))
    (at start (not(is_at ?agent ?init_loc)))
    (at start (not (agent_not_busy ?agent)))
    (at end (agent_not_busy ?agent))
    (at end (is_at ?tool ?end_loc))
    (at start (not(is_at ?tool ?init_loc)))
    )
)

(:durative-action execute_dynamic_action
 :parameters (?action - dynamic_action ?agent - agent ?init_loc - loc ?end_loc - loc)
 :duration (= ?duration 10)
 :condition (and
    (at start (agent_not_busy ?agent))
    (at start (is_at ?agent ?init_loc))
    (at start (action_loc ?action ?init_loc))
    (at start (action_end_loc ?action ?end_loc))
    (at start (handfree ?agent))
 )
 :effect (and
    (at start (not (handfree ?agent)))
    (at start (not (is_at ?agent ?init_loc)))
    (at end (handfree ?agent))
    (at start (not (agent_not_busy ?agent)))
    (at end (agent_not_busy ?agent))
    (at end (action_executed ?action ?agent))
    (at end (is_at ?agent ?end_loc))
    (at start (increase (total-cost ?agent) (action_cost ?agent ?action)))
    )
)

(:action take_tool
:parameters (?agent - agent ?tool - tool ?loc - loc)
:precondition (and 
    (handfree ?agent)
    (is_at ?tool ?loc)
    (is_at ?agent ?loc)
    (toolfree ?tool)
)
:effect (and
    (holding ?agent ?tool)
    (not (toolfree ?tool))
    (not (handfree ?agent))
)
)

(:action leave_tool
:parameters (?agent - agent ?tool - tool ?loc - loc)
:precondition (and
    (holding ?agent ?tool)
    (is_at ?agent ?loc)
)
:effect (and
    (handfree ?agent)
    (toolfree ?tool)
    (is_at ?tool ?loc)
    (not (holding ?agent ?tool))
)
)

(:durative-action execute_action_with_tool
 :parameters (?action - static_action_tool ?agent - agent ?loc - loc ?tool - tool)
 :duration (= ?duration 10)
 :condition (and
    (at start (agent_not_busy ?agent))
    (at start (is_at ?agent ?loc))
    (at start (action_loc ?action ?loc))
    (at start (action_tool ?action ?tool))
    (at start (holding ?agent ?tool))
 )
 :effect (and
    (at start (not (handfree ?agent)))
   ;  (at end (handfree ?agent)) ;-> now leave_tool
    (at start (not (agent_not_busy ?agent)))
    (at end (agent_not_busy ?agent))
    (at end (action_executed ?action ?agent))
   ;  (at end (not (holding ?agent ?tool))) ;-> now leave_tool
   ;  (at end (toolfree ?tool)) ;-> now leave_tool
    (at start (increase (total-cost ?agent) (action_cost ?agent ?action)))
    )
)

(:durative-action execute_dynamic_action_with_tool
 :parameters (?action - dynamic_action_tool ?agent - agent ?init_loc - loc ?end_loc - loc ?tool - tool)
 :duration (= ?duration 10)
 :condition (and
    (at start (agent_not_busy ?agent))
    (at start (is_at ?agent ?init_loc))
    (at start (action_loc ?action ?init_loc))
    (at start (action_end_loc ?action ?end_loc))
    (at start (action_tool ?action ?tool))
    (at start (holding ?agent ?tool))
 )
 :effect (and
    ; (at start (not (handfree ?agent)))
    (at start (not (is_at ?agent ?init_loc)))
    (at start (not (is_at ?tool ?init_loc)))

   ;  (at end (handfree ?agent)) ;-> now leave_tool
    (at start (not (agent_not_busy ?agent)))
    (at end (agent_not_busy ?agent))
    (at end (action_executed ?action ?agent))
   ;  (at end (not (holding ?agent ?tool))) ;-> now leave_tool
   ;  (at end (toolfree ?tool)) ;-> now leave_tool
    (at end (is_at ?agent ?end_loc))
    (at end (is_at ?tool ?end_loc))
    (at start (increase (total-cost ?agent) (action_cost ?agent ?action)))

    )
)

(:action finish_goal
 :parameters (?agent - agent ?goal - goal)
 :precondition (and
    (goal_pending ?goal)
    (forall (?action - action) (imply (goal_action ?goal ?action) (action_executed ?action ?agent)))
 )
 :effect (and
    (goal_finished ?goal)
    (not (goal_pending ?goal))
    (goal_executed ?goal ?agent)
)
)
)