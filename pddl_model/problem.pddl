(define (problem travel-01)
  (:domain travel-organizer)

  (:objects
    flight hotel taxi - item
    
    un920 so721 am659 un784 fr740 un741 so238 de523 am415 un722 so226 fr637 un250 am796 so886 - flight

    thelangham thegwen waldorfastoria hyattregency palmerhouse swissotel virginhotels congressplaza hotelfelix londonhouse intercontinental freehandchicago thedrake viceroychicago staypineapple - hotel

    uberx yellow-cab lyft-lux private-limo uber-black lyft curb - taxi

    denver chicago salt-lake-city dallas phoenix san-francisco - location

    c5 c10 c30 c4 c60 c35 c50 c88 c99 c130 c145 c160 c165 c175 c185 c189 c195 c210 c220 c225 c240 c245 c260 c275 c280 c290 c315 c320 c340 c380 c410 c450 c550 c650 c80 - cost

    ; (hh:mm format)
     t06-00 t07-55 t08-00 t08-30 t08-35 t08-45 t09-00 t09-30 t10-15 t10-30
      t11-00 t11-05 t11-15 t11-20 t11-30 t11-35 t12-00 t12-45 t12-50 t13-30
      t13-45 t13-50 t14-00 t14-05 t14-10 t14-35 t15-00 t15-30 t16-00 t16-20
      t16-45 t17-00 t17-45 t18-00 t18-05 t18-55 t19-00 t20-00 t20-20 t21-00
      t21-15 t21-20 t21-30 t22-00 t22-10 t22-50 t23-00 t23-30 t23-59 - time
    )

  (:init
    (flight-route fr637 denver chicago) (has-cost fr637 c88) (flight-times fr637 t12-00 t13-45)
    (flight-route un920 denver chicago) (has-cost un920 c245) (flight-times un920 t08-30 t11-05)
    (flight-route so721 denver chicago) (has-cost so721 c189) (flight-times so721 t10-15 t12-50)
    (flight-route am659 denver chicago) (has-cost am659 c210) (flight-times am659 t13-45 t16-20)
    (flight-route un784 denver chicago) (has-cost un784 c315) (flight-times un784 t16-20 t18-55)
    (flight-route fr740 denver chicago) (has-cost fr740 c99) (flight-times fr740 t06-00 t08-35)
    (flight-route un741 denver san-francisco) (has-cost un741 c280) (flight-times un741 t09-00 t11-35)
    (flight-route so238 denver chicago) (has-cost so238 c165) (flight-times so238 t14-10 t16-45)
    (flight-route de523 salt-lake-city chicago) (has-cost de523 c340) (flight-times de523 t11-30 t14-05)
    (flight-route am415 denver chicago) (has-cost am415 c195) (flight-times am415 t07-55 t10-30)
    (flight-route un722 denver chicago) (has-cost un722 c225) (flight-times un722 t11-15 t13-50)
    (flight-route so226 denver phoenix) (has-cost so226 c145) (flight-times so226 t08-45 t11-20)
    (flight-route un250 denver chicago) (has-cost un250 c275) (flight-times un250 t15-30 t18-05)
    (flight-route am796 dallas chicago) (has-cost am796 c260) (flight-times am796 t12-00 t14-35)
    (flight-route so886 denver chicago) (has-cost so886 c175) (flight-times so886 t17-45 t20-20)


;; it specifies that if you arrive at time x, what is the earliest available next taxi.
;; it’s also used for hotels to indicate that if you take a taxi at time x, you must arrive at the hotel for check-in at time y.

    (next-available t08-35 t09-00)    (next-available t08-35 t10-30)    (next-available t09-00 t10-30)    (next-available t09-00 t09-30)
    (next-available t12-50 t15-00)    (next-available t13-50 t16-00)    (next-available t13-45 t14-10)    (next-available t13-45 t16-45)
    (next-available t13-45 t21-15)    (next-available t14-10 t18-00)    (next-available t14-10 t16-00)    (next-available t11-05 t13-30)
    (next-available t14-10 t20-00)    (next-available t16-20 t18-05)    (next-available t16-45 t18-55)    (next-available t16-45 t18-00)
    (next-available t16-45 t20-00)    (next-available t16-45 t16-00)    (next-available t11-05 t11-20)    (next-available t12-50 t14-10)
    (next-available t13-50 t14-10)    (next-available t14-05 t14-10)    (next-available t14-35 t16-45)    (next-available t18-05 t21-15)
    (next-available t18-55 t21-15)    (next-available t20-20 t21-15)    (next-available t18-05 t20-20)    (next-available t18-55 t21-00)
    (next-available t20-20 t21-30)    (next-available t21-20 t22-00)    (next-available t22-10 t22-50)    (next-available t23-00 t23-30)
    (next-available t23-59 t23-59)    (next-available t11-20 t12-00)    (next-available t11-20 t13-30)    (next-available t14-10 t15-00)
    (next-available t14-10 t17-00)    (next-available t16-45 t17-00)    (next-available t16-45 t19-00)    (next-available t21-15 t22-00)

    (next-available t06-00 t08-00) (next-available t06-00 t09-30) (next-available t06-00 t10-30) (next-available t10-30 t11-20)
    (next-available t08-00 t08-00) (next-available t08-00 t09-30) (next-available t08-00 t10-30)
    (next-available t08-35 t09-30) (next-available t08-35 t11-00) (next-available t21-30 t22-00)
    (next-available t09-00 t11-00) (next-available t11-20 t14-00) (next-available t10-30 t12-45)
    (next-available t09-30 t09-30) (next-available t09-30 t10-30) (next-available t09-30 t11-00)
    (next-available t10-30 t11-00) (next-available t10-30 t12-00) (next-available t10-30 t13-30)
    (next-available t11-05 t12-00) (next-available t11-05 t14-00) (next-available t10-30 t20-20)
    (next-available t12-45 t13-30) (next-available t12-45 t14-00) (next-available t12-45 t15-00)
    (next-available t13-30 t14-00) (next-available t13-30 t15-00) (next-available t13-30 t16-00)
    (next-available t13-50 t14-00) (next-available t13-50 t15-00)
    (next-available t14-35 t15-00) (next-available t14-35 t16-00) (next-available t14-35 t17-00)
    (next-available t15-30 t16-00) (next-available t15-30 t17-00) (next-available t15-30 t18-00)
    (next-available t16-00 t17-00) (next-available t16-00 t18-00) (next-available t16-00 t19-00)
    (next-available t17-00 t18-00) (next-available t17-00 t19-00) (next-available t17-00 t20-00)
    (next-available t18-00 t19-00) (next-available t18-00 t20-00) (next-available t18-00 t21-00)
    (next-available t18-55 t19-00) (next-available t18-55 t20-00) (next-available t18-00 t22-00)
    (next-available t19-00 t19-00) (next-available t19-00 t20-00) (next-available t19-00 t21-00)
    (next-available t20-00 t20-00) (next-available t20-00 t21-00) (next-available t20-00 t22-00)
    (next-available t20-20 t21-00) (next-available t20-20 t22-00)


    (has-cost thelangham c550)     (has-check-in thelangham t11-00)
    (has-cost thegwen c80)  (has-check-in thegwen t14-00)
    (has-cost waldorfastoria c650)   (has-check-in waldorfastoria t15-00)
    (has-cost hyattregency c220)  (has-check-in hyattregency t16-00)
    (has-cost palmerhouse c50)  (has-check-in palmerhouse t12-00)
    (has-cost swissotel c240)   (has-check-in swissotel t13-30)
    (has-cost virginhotels c290)   (has-check-in virginhotels t17-00)
    (has-cost congressplaza c160)   (has-check-in congressplaza t18-00)
    (has-cost hotelfelix c145)  (has-check-in hotelfelix t08-00)
    (has-cost londonhouse c410)    (has-check-in londonhouse t19-00)
    (has-cost intercontinental c275)  (has-check-in intercontinental t20-00)
    (has-cost freehandchicago c130) (has-check-in freehandchicago t09-30)
    (has-cost thedrake c320)  (has-check-in thedrake t21-00)
    (has-cost viceroychicago c5)   (has-check-in viceroychicago t17-00)
    (has-cost staypineapple c10)  (has-check-in staypineapple t22-00)

    (has-cost uberx c30)
    (taxi-available uberx t09-00)
    (taxi-available uberx t13-30)
    (taxi-available uberx t18-00)
    (taxi-available uberx t23-00)

    (has-cost yellow-cab c30)
    (taxi-available yellow-cab t08-35)
    (taxi-available yellow-cab t12-45)
    (taxi-available yellow-cab t17-00)
    (taxi-available yellow-cab t21-15)

    (has-cost lyft c30)
    (taxi-available lyft t10-30)
    (taxi-available lyft t14-10)
    (taxi-available lyft t18-55)
    (taxi-available lyft t22-10)

    (has-cost curb c10)
    (taxi-available curb t18-00)
    (taxi-available curb t20-20)

    (has-cost lyft-lux c50)
    (taxi-available lyft-lux t09-30)
    (taxi-available lyft-lux t13-50)
    (taxi-available lyft-lux t16-45)
    (taxi-available lyft-lux t21-30)

    (has-cost private-limo c60)
    (taxi-available private-limo t08-00)
    (taxi-available private-limo t14-35)
    (taxi-available private-limo t19-00)
    (taxi-available private-limo t23-00)

    (has-cost uber-black c50)
    (taxi-available uber-black t11-05)
    (taxi-available uber-black t15-30)
    (taxi-available uber-black t20-00)
    (taxi-available uber-black t22-50)

    (is-origin denver)
    (is-destination chicago)
  )

(:goal (and
        (any-flight-booked)
        (any-hotel-booked)
        (any-taxi-booked)
    )
   )
)
