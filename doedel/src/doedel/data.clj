(ns doedel.data
  (:use clojure.edn)
  (:require [doedel.util :as util]))

(def ^:dynamic *users*)
(def prefix (atom ""))

(defn generate-patterns [num-patterns length]
  (letfn [(gen-pattern []
            (apply str (repeatedly length #(case (rand-int 2)
                                             0 "L" 1 "H"))))]
    (loop [patterns []]
      (if (= num-patterns (count patterns))
        patterns
        (let [pattern (gen-pattern)]
          (recur (if (some #{pattern} patterns)
                   ;; If pattern is already present don't add it again
                   patterns
                   (conj patterns pattern))))))))

(defn register-user [input output-writer]
  (let [user-id (:user-id input)
        token (:security-token input)]
    ;; Check if user-id is present and, that it is assigned to this server
    ;; (by having the right prefix)
    (if (and user-id (or (.equals @prefix "") (.startsWith user-id @prefix)) token)
        (let [num-patterns 3
              pattern-length 5
              patterns (generate-patterns num-patterns pattern-length)
              init-pattern-map (apply hash-map
                                      (conj (vec (interpose nil patterns)) nil))]
          (swap! *users* assoc user-id {:patterns init-pattern-map
                                        :token token})
          (.write output-writer (str {:response-type :success
                                      :user-id user-id}))))))

(defn get-patterns [input output-writer]
  (when-let [user-id (:user-id input)]
    (when (contains? @*users* user-id)
      (let [user (@*users* user-id)
            token (:token user)
            patterns (vec (doall (map first (:patterns user))))]
        (.write output-writer (str {:response-type :vibrate
                                    :security-token token
                                    :patterns patterns}))))))

(defn data-transmission [input output-writer]
  (let [{:keys [user-id pattern excitement-level]} input]
    ;; Check if necessary fields are present
    (when (and user-id pattern excitement-level
               (number? excitement-level)
               (contains? @*users* user-id)
               (contains? (:patterns (@*users* user-id)) pattern))
      (swap! *users* assoc-in [user-id :patterns pattern] excitement-level)
      (.write output-writer (str {:response-type :success
                                  :security-token (:token (@*users* user-id))})))))

(defn fun-time [input output-writer]
  ;; For every user check if the customer has been successfully
  ;; evaluated and if so let her have some fun with the
  ;; best matching pattern.

  (let [user-id (:user-id input)]
    ;; Check if user exists
    (when (contains? @*users* user-id)
      ;; Check if all test patterns have been evaluated
      ;; i.e. every value (second item in element when seq'ed)
      ;; for each entry in the map is non-nil
      (let [test-map (:patterns (@*users* user-id))]
        (when (every? second test-map)
          ;; If so look for the best excitement level
          (.write output-writer (str {:response-type :vibrate
                                      :pattern (key (apply max-key val test-map))
                                      :user-id user-id
                                      :security-token (:token (@*users* user-id))})))))))

(defn data-handler [port]
  (binding [*users* (atom {})]
    (letfn [(handler-fn [input-reader output-writer]
              ;; XXX: Be sure NOT to use clojure.core/read,
              ;; but clojure.edn/read as the former would allow
              ;; trival RCE attacks!
              ;; For that matter we _use_ edn in our ns form
              (let [input (read input-reader)
                    {:keys [request-type]} input]
                (when request-type
                  (case request-type
                    :register-user (register-user input output-writer)
                    :get-patterns (get-patterns input output-writer)
                    :send-data (data-transmission input output-writer)
                    :get-best-pattern (fun-time input output-writer)
                    (.write output-writer (str {:response-type :error}))))))]
      (util/handler handler-fn port))))
