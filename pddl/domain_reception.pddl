(define (domain reception_domain)

(:requirements :typing :durative-actions :fluents :negative-preconditions :action-costs :strips)
(:types agent loc obj) ; 3 types: agents, locations, objects

(:predicates
   ;  (agent_busy ?agent - agent)
    (agent_not_busy ?agent - agent)

    ; goals are formed as: predicate object location
    ; one predicate asociated to one action
    (is_into_box ?obj - obj ?loc - loc)
    (stamped ?obj - obj ?loc - loc)
    (picked_up ?obj - obj ?loc - loc)
)

(:functions
    ; each action has an associated cost
    (stamp_cost ?agent - agent ?obj - obj ?loc - loc)
    (put_cost ?agent - agent ?obj - obj ?loc - loc)
    (pick_up_cost ?agent - agent ?obj - obj ?loc - loc)
    (total-cost)
)

; each action has its associated predicate as an effect
; each action has 3 params: agent, object, location


(:durative-action stamp
 :parameters (?agent - agent ?obj - obj ?loc - loc)
 :duration (= ?duration 10)
 :condition (and
    (at start (agent_not_busy ?agent))
    )
 :effect (and
    
    (at end (stamped ?obj ?loc))
   ;  (at start (agent_busy ?agent))
    (at start (not (agent_not_busy ?agent)))
   ;  (at end (not (agent_busy ?agent)))
    (at end (agent_not_busy ?agent))

    (at start (increase (total-cost) (stamp_cost ?agent ?obj ?loc)))
    )
)

(:durative-action pick_up
 :parameters (?agent - agent ?obj - obj ?loc - loc)
 :duration (= ?duration 10)
 :condition (and
    (at start (agent_not_busy ?agent))
    )
 :effect (and
    
    (at end (picked_up ?obj ?loc))
   ;  (at start (agent_busy ?agent))
    (at start (not (agent_not_busy ?agent)))
   ;  (at end (not (agent_busy ?agent)))
    (at end (agent_not_busy ?agent))

    (at start (increase (total-cost) (pick_up_cost ?agent ?obj ?loc)))
    )
)

(:durative-action put
 :parameters (?agent - agent ?obj - obj ?loc - loc)
 :duration (= ?duration 10)
 :condition (and
    (at start (agent_not_busy ?agent))
    )
 :effect (and
    
    (at end (is_into_box ?obj ?loc))
   ;  (at start (agent_busy ?agent))
    (at start (not (agent_not_busy ?agent)))
   ;  (at end (not (agent_busy ?agent)))
    (at end (agent_not_busy ?agent))

    (at start (increase (total-cost) (put_cost ?agent ?obj ?loc)))
    )
)
)