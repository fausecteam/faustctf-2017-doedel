(ns doedel.status
  (:use clojure.edn)
  (:require [doedel.util :as util])
  (:import [java.net InetAddress]))

(defn status-handler [port]
  (let [hostname (.getHostName (InetAddress/getLocalHost))]
    (letfn [(handler-fn [input-reader output-writer]
              (let [request (read input-reader)]
                (spit output-writer
                      (if (= request {:request-type :status})
                        (str {:response-type :status
                              :clojure-version 1.7
                              :hostname hostname
                              :banner "  ____                      _  \n (|   \\             |      | | \n |    | __   _   __|   _  | | \n _|    |/  \\_|/  /  |  |/  |/  \n (/\\___/ \\__/ |__/\\_/|_/|__/|__/\n"
                              })
                        (str {:response-type :error})))))]
      (util/handler handler-fn port))))
