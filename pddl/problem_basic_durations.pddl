(define (problem problem_basic_duration)
(:domain domain_basic_duration)

(:objects
    human robot - agent
    loc1 loc2 - loc
    stamp_diplomas recieve_package attend_visitant takeout_trash - action
)

(:init
    (agent_not_busy robot)
    (agent_not_busy human)

    (is_at human loc1)
    (is_at robot loc2)

    (action_loc stamp_diplomas loc1)
    (action_end_loc stamp_diplomas loc1)
    (action_loc recieve_package loc2)
    (action_end_loc recieve_package loc1)
    (action_loc attend_visitant loc2)
    (action_end_loc attend_visitant loc2)
    (action_loc takeout_trash loc2)
    (action_end_loc takeout_trash loc2)

    (=(action_duration human stamp_diplomas) 15)
    (=(action_duration robot stamp_diplomas) 10)
    (=(action_duration human recieve_package) 20)
    (=(action_duration robot recieve_package) 10)
    (=(action_duration human attend_visitant) 15)
    (=(action_duration robot attend_visitant) 15)
    (=(action_duration human takeout_trash) 15)
    (=(action_duration robot takeout_trash) 20)

    (=(action_cost human stamp_diplomas) 20)
    (=(action_cost robot stamp_diplomas) 0)
    (=(action_cost human recieve_package) 0)
    (=(action_cost robot recieve_package) 0)
    (=(action_cost human attend_visitant) 0)
    (=(action_cost robot attend_visitant) 20)
    (=(action_cost robot takeout_trash) 20)
    (=(action_cost human takeout_trash) 20)

    (= (total-cost robot) 0)
    (= (total-cost human) 0)
)
(:goal (and
    (action_done stamp_diplomas)
    (action_done recieve_package)
    (action_done attend_visitant)
    (action_done takeout_trash)
    ))
(:metric minimize (+ (* 1 (total-cost robot))(* 1 (total-cost human))(* 1 (total-time))))
)
