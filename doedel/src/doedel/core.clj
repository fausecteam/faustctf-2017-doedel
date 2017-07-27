(ns doedel.core
  (:require [doedel.status :as status]
            [doedel.data :as data]
            [doedel.util :as util]
            [clojure.core.async :refer :all])
  (:gen-class))

(defn -main [& args]
  (go (data/data-handler 1666))
  (go (status/status-handler 1667))
  (loop []
    (Thread/sleep Long/MAX_VALUE)
    (recur)))
