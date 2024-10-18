(define (problem problem_simple)
(:domain domain_simple)

(:objects
    human robot - agent
    loc1 loc2 - loc
    stamp_diplomas - action
)

(:init
    (agent_not_busy robot)
    (agent_not_busy human)
    (is_at human loc1)
    (is_at robot loc2)
    (action_loc stamp_diplomas loc1)
    (=(action_cost human stamp_diplomas) 50)
    (=(action_cost robot stamp_diplomas) 25)
    (= (total-cost) 0)
)

(:goal (and
    (action_executed stamp_diplomas)
    ))
(:metric minimize (+ (* 1 (total-cost))(* 1 (total-time))))
)
