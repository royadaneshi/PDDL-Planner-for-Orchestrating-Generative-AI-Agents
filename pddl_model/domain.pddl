(define (domain travel-organizer)
(:requirements :strips :typing :negative-preconditions :conditional-effects)

  (:types
    flight hotel taxi - item
    location cost time - object
    item - object
  )


  (:predicates
    (flight-route ?f - flight ?from ?to - location)
    (flight-times ?f - flight ?dep ?arr - time)
    (has-cost ?option - item ?c - cost)
    (has-check-in ?h - hotel ?t - time)
    (taxi-available ?t - taxi ?t-start - time)
    (any-flight-booked)
    (any-hotel-booked)
    (any-taxi-booked)
    (flight-cost-booked ?c - cost)
    (hotel-cost-booked ?c - cost)
    (next-available ?t1 ?t2 - time)

    (is-origin ?l - location)
    (is-destination ?l - location)

    (taxi-booked-for ?t - taxi ?avail - time)
    (flight-booked-for ?f - flight ?arr - time)
    (hotel-booked-for ?h - hotel ?check-in - time)
  )

  (:action book-flight
    :parameters (?f - flight ?arr - time ?c - cost ?from ?to - location ?dep - time)
    :precondition (and
        (flight-route ?f ?from ?to)
        (is-origin ?from)
        (has-cost ?f ?c)
        (is-destination ?to)
        (flight-times ?f ?dep ?arr)
        (not (any-flight-booked))
    )
    :effect (and
        (flight-booked-for ?f  ?arr)
        (any-flight-booked)
    )
  )

 (:action book-hotel
    :parameters (?h - hotel ?checkin - time ?c - cost ?t - taxi ?taxi-time - time)
    :precondition (and
        (taxi-booked-for ?t ?taxi-time)
        (has-check-in ?h ?checkin)
        (has-cost ?h ?c)
        (next-available ?taxi-time ?checkin)
        (not (any-hotel-booked))
    )
    :effect (and
        (hotel-booked-for ?h ?checkin)
        (any-hotel-booked)
    )
  )

(:action book-taxi
    :parameters (?t - taxi ?avail - time ?c - cost ?f - flight ?arr - time)
    :precondition (and
        (flight-booked-for ?f  ?arr)
        (next-available ?arr ?avail)
        (has-cost ?t ?c)
        (taxi-available ?t ?avail)
        (not (any-taxi-booked))
    )
    :effect (and
        (any-taxi-booked)
        (taxi-booked-for ?t ?avail)
    )
)
)