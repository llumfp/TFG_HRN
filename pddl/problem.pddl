(define (problem problem_simple)
(:domain domain_simple)

(:objects
    human robot - agent
    loc1 loc2 - loc
    stamp_diplomas - static_action
    recieve_package - dynamic_action
    open_package - static_action_tool
    move_box - dynamic_action_tool
    cutter cart - tool
)

(:init
    (agent_not_busy robot)
    (agent_not_busy human)
    (is_at human loc1)
    (is_at robot loc2)
    (handfree robot)
    (handfree human)
    (is_at cutter loc2)
    (is_at cart loc2)
    (action_loc stamp_diplomas loc1)
    (action_loc recieve_package loc2)
    (action_end_loc recieve_package loc1)
    (action_loc open_package loc2)
    (action_tool open_package cutter)
    (action_tool move_box cart)
    (action_loc move_box loc1)
    (action_end_loc move_box loc2)
    (=(action_cost human stamp_diplomas) 50)
    (=(action_cost robot stamp_diplomas) 25)
    (=(action_cost human recieve_package) 100)
    (=(action_cost robot recieve_package) 100)
    (=(action_cost human open_package) 10)
    (=(action_cost robot open_package) 100)
    (=(action_cost robot move_box) 10)
    (=(action_cost human move_box) 20)
    (= (total-cost robot) 0)
    (= (total-cost human) 0)
)

(:goal (and
    (action_executed stamp_diplomas)
    (action_executed recieve_package)
    (action_executed open_package)
    (action_executed move_box)
    ))
(:metric minimize (+ (* 1 (total-cost robot))(* 1 (total-cost human))(* 1 (total-time))))
)
