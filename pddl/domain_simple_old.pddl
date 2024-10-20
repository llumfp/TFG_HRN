(define (domain domain_simple_old)

(:requirements :typing :durative-actions :fluents :negative-preconditions :action-costs :strips)
(:types agent loc action
    dynamic_action static_action - action
)

(:predicates
    (agent_not_busy ?agent - agent)
    (is_at ?agent - agent ?loc - loc)
    (action_executed ?action - action)
    (action_loc ?action - action ?loc - loc)
    (action_end_loc ?action - dynamic_action ?loc - loc)
)

(:functions
    ; each action has an associated cost
    (action_cost ?agent - agent ?action - action)
    (total-cost)
)

(:durative-action execute_action
 :parameters (?action - static_action ?agent - agent ?loc - loc)
 :duration (= ?duration 10)
 :condition (and
    (at start (agent_not_busy ?agent))
    (at start (is_at ?agent ?loc))
    (at start (action_loc ?action ?loc))
    )

 :effect (and
    (at start (not (agent_not_busy ?agent)))
    (at end (agent_not_busy ?agent))
    (at end (action_executed ?action))
    (at start (increase (total-cost) (action_cost ?agent ?action)))
    )
)

(:durative-action move_to_loc
 :parameters (?agent - agent ?init_loc - loc ?end_loc - loc)
 :duration (= ?duration 10)
 :condition (and
    (at start (agent_not_busy ?agent))
    (at start (is_at ?agent ?init_loc))
 )
 :effect (and
    (at end (is_at ?agent ?end_loc))
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
 )
 :effect (and
    (at start (not (agent_not_busy ?agent)))
    (at end (agent_not_busy ?agent))
    (at end (action_executed ?action))
    (at end (is_at ?agent ?end_loc))
    (at start (increase (total-cost) (action_cost ?agent ?action)))
    )
)
)