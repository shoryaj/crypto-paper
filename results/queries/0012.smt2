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
 (> 100.0 0.0))
(assert
 (> 100.0 0.0))
(assert
 (>= f 0.0))
(assert
 (>= a_out 0.0))
(assert
 (> 100.0 a_out))
(assert
 (= (* (+ 100.0 f) (- 100.0 a_out)) (* 100.0 100.0)))
(assert
 (let ((?x40 (+ 100.0 f)))
 (= (* spot_price (- 100.0 a_out)) ?x40)))
(assert
 (let ((?x41 (- 100.0 a_out)))
 (> ?x41 0.0)))
(assert
 (let ((?x40 (+ 100.0 f)))
 (> ?x40 0.0)))
(assert
 (>= a_out 0.0))
(assert
 (>= b_return 0.0))
(assert
 (let ((?x40 (+ 100.0 f)))
 (< b_return ?x40)))
(assert
 (= (* (+ (- 100.0 a_out) a_out) (- (+ 100.0 f) b_return)) (* (- 100.0 a_out) (+ 100.0 f))))
(assert
 (>= borrow 0.0))
(assert
 (>= 400.0 borrow))
(assert
 (<= borrow (* (* 100.0 spot_price) (/ 11.0 20.0))))
(assert
 (let ((?x244 (- (+ borrow b_return) (* f (+ 1.0 (/ 3.0 2000.0))))))
 (>= ?x244 0.0)))
(assert
 (let ((?x244 (- (+ borrow b_return) (* f (+ 1.0 (/ 3.0 2000.0))))))
(let ((?x121 (- ?x244 (* 100.0 (/ 100.0 100.0)))))
(> ?x121 0.0))))
(check-sat)
