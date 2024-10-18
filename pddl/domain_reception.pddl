(define (domain reception_domain)

(:requirements :typing :durative-actions :fluents :negative-preconditions :action-costs :strips)
(:types agent loc action tool) ; 3 types: agents, locations, actions, tools

(:predicates
    (agent_not_busy ?agent - agent)
    (action_done ?agent - agent ?action - action)
    (is_at ?agent - agent ?loc - loc)
    (hand_free ?agent - agent)
    (holding ?agent - agent ?tool - tool)
    (goal_reached ?agent - agent ?goal - goal)
)

(:functions
    (action_cost ?agent - agent ?action - action ?loc - loc)
    (duration_action ?action - action ?agent - agent)
    (total-cost)
)

(:durative-action basic_action
    :parameters (?agent - agent ?action - action ?loc - loc)
    :duration (= ?duration (duration_action ?action ?agent))
    :condition (and
        (at start (and (agent_not_busy ?agent) (hand_free ?agent) (is_at ?agent ?loc)))
    )
    :effect (and 
        (at start (and 
            (not (agent_not_busy ?agent)) 
            (increase (total-cost) (action_cost ?agent ?action ?loc))
        ))
        (at end (and 
            (action_done ?agent ?action)
            (agent_not_busy ?agent)
        ))
    )
)

(:durative-action dynamic_action
    :parameters (?agent - agent ?action - action ?start_loc - loc ?end_loc - loc)
    :duration (= ?duration (duration_action ?action ?agent))
    :condition (and
        (at start (and (agent_not_busy ?agent) (hand_free ?agent) (is_at ?agent ?start_loc)))
    )
    :effect (and 
        (at start (and 
            (not (agent_not_busy ?agent)) 
            (increase (total-cost) (action_cost ?agent ?action ?start_loc))
        ))
        (at end (and 
            (action_done ?agent ?action)
            (agent_not_busy ?agent)
            (is_at ?agent ?end_loc)
        ))
    )
)

(:durative-action action_with_tool
    :parameters (?agent - agent ?action - action ?loc - loc ?tool - tool)
    :duration (= ?duration (duration_action ?action ?agent))
    :condition (and
        (at start (and (agent_not_busy ?agent) (is_at ?agent ?loc) (holding ?agent ?tool)))
    ) 
    :effect (and 
        (at start (and 
            (not (agent_not_busy ?agent)) 
            (increase (total-cost) (action_cost ?agent ?action ?loc))
        ))
        (at end (and 
            (action_done ?agent ?action)
            (agent_not_busy ?agent)
            (not (holding ?agent ?tool))
            (hand_free ?agent)
        ))
    )
)

(:action pick_up_tool
    :parameters (?agent - agent ?tool - tool ?loc - loc)
    :precondition (and (agent_not_busy ?agent) (hand_free ?agent) (is_at ?agent ?loc) (is_at ?tool ?loc))
    :effect (and (holding ?agent ?tool) (not (hand_free ?agent)))
)

(:durative-action dynamic_action_with_tool
    :parameters (?agent - agent ?action - action ?start_loc - loc ?end_loc - loc ?tool - tool)
    :duration (= ?duration (duration_action ?action ?agent))
    :condition (and
        (at start (and (agent_not_busy ?agent) (is_at ?agent ?start_loc) (holding ?agent ?tool)))
    ) 
    :effect (and 
        (at start (and 
            (not (agent_not_busy ?agent)) 
            (increase (total-cost) (action_cost ?agent ?action ?start_loc))
        ))
        (at end (and 
            (action_done ?agent ?action)
            (agent_not_busy ?agent)
            (not (holding ?agent ?tool))
            (hand_free ?agent)
            (is_at ?agent ?end_loc)
        ))
    )
)
)