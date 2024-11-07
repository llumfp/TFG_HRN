(define (domain domain_basic_duration)

(:requirements :durative-actions :negative-preconditions :action-costs :adl)
(:types agent loc action tool goal
)
 
(:predicates
    (agent_not_busy ?agent - agent)

    (is_at ?agent - agent ?loc - loc)
    (action_executed ?action - action ?agent - agent)
    (action_done ?action - action)
     
    (action_loc ?action - action ?loc - loc)
    (action_end_loc ?action - action ?loc - loc)
)

(:functions
    ; each action has an associated cost
    (action_cost ?agent - agent ?action - action)
    (action_duration ?agent - agent ?action - action)
    (total-cost ?agent - agent)
)

(:durative-action move_to_loc
 :parameters (?agent - agent ?init_loc - loc ?end_loc - loc)
 :duration (= ?duration 5)
 :condition (and
    (at start (agent_not_busy ?agent))
    (at start (is_at ?agent ?init_loc))
 )
 :effect (and
    (at end (is_at ?agent ?end_loc))
    (at start (not (is_at ?agent ?init_loc)))
    (at start (not (agent_not_busy ?agent)))
    (at end (agent_not_busy ?agent))
    )
)

(:durative-action execute_action
 :parameters (?action - action ?agent - agent ?init_loc - loc ?end_loc - loc)
 :duration (= ?duration (action_duration ?agent ?action))
 :condition (and
    (at start (agent_not_busy ?agent))
    (at start (is_at ?agent ?init_loc))
    (at start (action_loc ?action ?init_loc))
    (at start (action_end_loc ?action ?end_loc))
 )
 :effect (and
    (at start (not (is_at ?agent ?init_loc)))
    (at start (not (agent_not_busy ?agent)))
    (at end (agent_not_busy ?agent))
    (at end (action_executed ?action ?agent))
    (at end (action_done ?action))
    (at end (is_at ?agent ?end_loc))
    (at start (increase (total-cost ?agent) (action_cost ?agent ?action)))
    )
)

)