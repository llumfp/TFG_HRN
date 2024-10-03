(define (domain kitchen_collab_domain)

(:requirements :typing :durative-actions :fluents :negative-preconditions :action-costs :strips)
(:types agent loc obj) ; 3 types: agents, locations, objects

(:predicates
   ;  (agent_busy ?agent - agent)
    (agent_not_busy ?agent - agent)

    ; goals are formed as: predicate object location
    ; one predicate asociated to one action
    (stored ?obj - obj ?loc - loc)
    (used_to_clean ?obj - obj ?loc - loc)
    (served_as_snack ?obj - obj ?loc - loc)
    (cooked ?obj - obj ?loc - loc)
)

(:functions
    ; each action has an associated cost
    (stored_cost ?agent - agent ?obj - obj ?loc - loc)
    (used_to_clean_cost ?agent - agent ?obj - obj ?loc - loc)
    (served_as_snack_cost ?agent - agent ?obj - obj ?loc - loc)
    (cooked_cost ?agent - agent ?obj - obj ?loc - loc)
    (total-cost)
)

; each action has its associated predicate as an effect
; each action has 3 params: agent, object, location

(:durative-action store
 :parameters (?agent - agent ?obj - obj ?loc - loc)
 :duration (= ?duration 10)
 :condition (and
    (at start (agent_not_busy ?agent))
    )
 :effect (and
    
    (at end (stored ?obj ?loc))
   ;  (at start (agent_busy ?agent))
    (at start (not (agent_not_busy ?agent)))
   ;  (at end (not (agent_busy ?agent)))
    (at end (agent_not_busy ?agent))

    (at start (increase (total-cost) (stored_cost ?agent ?obj ?loc)))
    )
)

(:durative-action serve
 :parameters (?agent - agent ?obj - obj ?loc - loc)
 :duration (= ?duration 10)
 :condition (and
    (at start (agent_not_busy ?agent))
    )
 :effect (and
    
    (at end (served_as_snack ?obj ?loc))
   ;  (at start (agent_busy ?agent))
    (at start (not (agent_not_busy ?agent)))
   ;  (at end (not (agent_busy ?agent)))
    (at end (agent_not_busy ?agent))

    (at start (increase (total-cost) (served_as_snack_cost ?agent ?obj ?loc)))
    )
)

(:durative-action clean
 :parameters (?agent - agent ?obj - obj ?loc - loc)
 :duration (= ?duration 10)
 :condition (and
    (at start (agent_not_busy ?agent))
    )
 :effect (and
    
    (at end (used_to_clean ?obj ?loc))
   ;  (at start (agent_busy ?agent))
    (at start (not (agent_not_busy ?agent)))
   ;  (at end (not (agent_busy ?agent)))
    (at end (agent_not_busy ?agent))

    (at start (increase (total-cost) (used_to_clean_cost ?agent ?obj ?loc)))
    )
)

(:durative-action cook
 :parameters (?agent - agent ?obj - obj ?loc - loc)
 :duration (= ?duration 10)
 :condition (and
    (at start (agent_not_busy ?agent))
    )
 :effect (and
    
    (at end (cooked ?obj ?loc))
   ;  (at start (agent_busy ?agent))
    (at start (not (agent_not_busy ?agent)))
   ;  (at end (not (agent_busy ?agent)))
    (at end (agent_not_busy ?agent))

    (at start (increase (total-cost) (cooked_cost ?agent ?obj ?loc)))
    )
)

)