(defproject doedel "0.1.0-SNAPSHOT"
  :dependencies [[org.clojure/clojure "1.8.0"]
                 [org.clojure/core.async "0.2.391"]]
  :main ^:skip-aot doedel.core
  :target-path "target/"
  :uberjar-name "doedel.jar"
  :profiles {:uberjar {:aot :all}})
