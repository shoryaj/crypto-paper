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
 (> 1000.0 0.0))
(assert
 (> 1000.0 0.0))
(assert
 (>= f 0.0))
(assert
 (>= a_out 0.0))
(assert
 (> 1000.0 a_out))
(assert
 (= (* (+ 1000.0 f) (- 1000.0 a_out)) (* 1000.0 1000.0)))
(assert
 (let ((?x236 (+ 1000.0 f)))
 (= (* spot_price (- 1000.0 a_out)) ?x236)))
(assert
 (let ((?x149 (- 1000.0 a_out)))
 (> ?x149 0.0)))
(assert
 (let ((?x236 (+ 1000.0 f)))
 (> ?x236 0.0)))
(assert
 (>= a_out 0.0))
(assert
 (>= b_return 0.0))
(assert
 (let ((?x236 (+ 1000.0 f)))
 (< b_return ?x236)))
(assert
 (= (* (+ (- 1000.0 a_out) a_out) (- (+ 1000.0 f) b_return)) (* (- 1000.0 a_out) (+ 1000.0 f))))
(assert
 (>= borrow 0.0))
(assert
 (>= 400.0 borrow))
(assert
 (<= borrow (* (* 100.0 spot_price) (/ 19.0 20.0))))
(assert
 (let ((?x174 (- (+ borrow b_return) (* f (+ 1.0 (/ 3.0 2000.0))))))
 (>= ?x174 0.0)))
(assert
 (let ((?x174 (- (+ borrow b_return) (* f (+ 1.0 (/ 3.0 2000.0))))))
(let ((?x148 (- ?x174 (* 100.0 (/ 1000.0 1000.0)))))
(> ?x148 0.0))))
(check-sat)
