(define (domain domain_very_basic)

(:requirements :durative-actions :negative-preconditions :action-costs :adl)
(:types agent loc action tool goal
)
 
(:predicates
    (agent_not_busy ?agent - agent)
    (action_executed ?action - action ?agent - agent)
    (action_done ?action - action)
)

(:functions
    ; each action has an associated cost
    (action_cost ?agent - agent ?action - action)
    (total-cost ?agent - agent)
)

(:durative-action execute_action
 :parameters (?action - action ?agent - agent ?init_loc - loc ?end_loc - loc)
 :duration (= ?duration 10)
 :condition (and
    (at start (agent_not_busy ?agent))
 )
 :effect (and
    (at start (not (agent_not_busy ?agent)))
    (at end (agent_not_busy ?agent))
    (at end (action_executed ?action ?agent))
    (at end (action_done ?action))
    (at start (increase (total-cost ?agent) (action_cost ?agent ?action)))
    )
)

)