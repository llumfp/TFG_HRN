(define (domain domain_simple)

(:requirements :typing :durative-actions :fluents :negative-preconditions :action-costs :strips)
(:types agent loc action tool - object
    dynamic_action static_action static_action_tool dynamic_action_tool - action
)
 
(:predicates
    (agent_not_busy ?agent - agent)
    (holding ?agent - agent ?tool - tool)
    (handfree ?agent - agent)

    (is_at ?obj - object ?loc - loc)
    (action_executed ?action - action)
     
    (action_loc ?action - action ?loc - loc)
    (action_end_loc ?action - action ?loc - loc)
    (action_tool ?action - action ?tool - tool)
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
    (at end (action_executed ?action))
    (at start (increase (total-cost ?agent) (action_cost ?agent ?action)))
    )
)

(:durative-action move_to_loc
 :parameters (?agent - agent ?init_loc - loc ?end_loc - loc)
 :duration (= ?duration 10)
 :condition (and
    (at start (agent_not_busy ?agent))
    (at start (is_at ?agent ?init_loc))
    ; (at start (handfree ?agent))
 )
 :effect (and
    (at end (is_at ?agent ?end_loc))
    (at end (not(is_at ?agent ?init_loc)))
    (at start (not (agent_not_busy ?agent)))
    (at end (agent_not_busy ?agent))
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
    (at end (handfree ?agent))
    (at start (not (agent_not_busy ?agent)))
    (at end (agent_not_busy ?agent))
    (at end (action_executed ?action))
    (at end (not(is_at ?agent ?init_loc)))
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
)
:effect (and
    (holding ?agent ?tool)
    (not (handfree ?agent))
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
    (at end (handfree ?agent))
    (at start (not (agent_not_busy ?agent)))
    (at end (agent_not_busy ?agent))
    (at end (action_executed ?action))
    (at end (not (holding ?agent ?tool)))
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
    (at start (not (handfree ?agent)))
    (at end (handfree ?agent))
    (at start (not (agent_not_busy ?agent)))
    (at end (agent_not_busy ?agent))
    (at end (action_executed ?action))
    (at end (not (holding ?agent ?tool)))
    (at end (is_at ?agent ?end_loc))
    (at end (is_at ?tool ?end_loc))
    (at start (increase (total-cost ?agent) (action_cost ?agent ?action)))
    )
)

)