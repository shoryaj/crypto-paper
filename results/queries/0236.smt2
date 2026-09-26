; benchmark generated from python API
(set-info :status unknown)
(declare-fun f () Real)
(declare-fun a_out () Real)
(declare-fun spot_price () Real)
(declare-fun b_return () Real)
(declare-fun borrow () Real)
(assert
 (> f 0.0))
(assert
 (>= 1000.0 f))
(assert
 (> 10000.0 0.0))
(assert
 (> 10000.0 0.0))
(assert
 (>= f 0.0))
(assert
 (>= a_out 0.0))
(assert
 (> 10000.0 a_out))
(assert
 (= (* (+ 10000.0 f) (- 10000.0 a_out)) (* 10000.0 10000.0)))
(assert
 (let ((?x137 (+ 10000.0 f)))
 (= (* spot_price (- 10000.0 a_out)) ?x137)))
(assert
 (let ((?x39 (- 10000.0 a_out)))
 (> ?x39 0.0)))
(assert
 (let ((?x137 (+ 10000.0 f)))
 (> ?x137 0.0)))
(assert
 (>= a_out 0.0))
(assert
 (>= b_return 0.0))
(assert
 (let ((?x137 (+ 10000.0 f)))
 (< b_return ?x137)))
(assert
 (= (* (+ (- 10000.0 a_out) a_out) (- (+ 10000.0 f) b_return)) (* (- 10000.0 a_out) (+ 10000.0 f))))
(assert
 (>= borrow 0.0))
(assert
 (>= 400.0 borrow))
(assert
 (<= borrow (* (* 100.0 spot_price) (/ 4.0 5.0))))
(assert
 (let ((?x81 (- (+ borrow b_return) (* f (+ 1.0 (/ 9.0 10000.0))))))
 (>= ?x81 0.0)))
(assert
 (let ((?x81 (- (+ borrow b_return) (* f (+ 1.0 (/ 9.0 10000.0))))))
(let ((?x110 (- ?x81 (* 100.0 (/ 10000.0 10000.0)))))
(> ?x110 0.0))))
(check-sat)
