(ns doedel.util
  (:import [java.net InetAddress InetSocketAddress ServerSocket]
           [java.io PushbackReader])
  (:require [clojure.java.io :as io]
            [clojure.core.async :refer [thread]]))

(defn get-hostname []
  (.getHostName (InetAddress/getLocalHost)))

(defn handler [handler-fn port]
  (let [socket (ServerSocket.)]
    (.setReuseAddress socket true)
    ;; TODO: fix address to 0.0.0.0
    (.bind socket (InetSocketAddress. "127.0.0.1" port))
    ;; Spawn 32 worker to handle incoming connections
    (dotimes [_ 32]
      (thread
        (loop []
            (let [client-socket (.accept socket)
                  input-reader (PushbackReader. (io/reader (.getInputStream client-socket)))
                  output-writer (io/writer (.getOutputStream client-socket))]
              (try
                (.setSoTimeout client-socket 2000)
                (handler-fn input-reader output-writer)
                (.flush output-writer)
                (.close output-writer)
                (.close client-socket)
                (catch Exception e
                  (.close client-socket)
                  (prn "Failed to talk to client. Exception: " e))))
            (recur))))))
