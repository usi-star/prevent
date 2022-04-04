graph [
    directed 1
    node [
        id 0
        Node "RES0"
        dataSourceType "n.a."
        label "RES0_M0"
        metric "M0"
        resource "RES0"
    ]
    node [
        id 1
        Node "RES0"
        dataSourceType "n.a."
        label "RES0_M1"
        metric "M1"
        resource "RES0"
    ]
    node [
        id 2
        Node "RES0"
        dataSourceType "n.a."
        label "RES0_M2"
        metric "M2"
        resource "RES0"
    ]
    node [
        id 3
        Node "RES1"
        dataSourceType "n.a."
        label "RES1_M0"
        metric "M0"
        resource "RES1"
    ]
    node [
        id 4
        Node "RES1"
        dataSourceType "n.a."
        label "RES1_M1"
        metric "M1"
        resource "RES1"
    ]
    node [
        id 5
        Node "RES2"
        dataSourceType "n.a."
        label "RES2_M0"
        metric "M0"
        resource "RES2"
    ]
    edge [
        source 1
        target 0
        weight 0.1
    ]
    edge [
        source 2
        target 0
        weight 0.0
    ]
    edge [
        source 3
        target 0
        weight 0.11
    ]
    edge [
        source 2
        target 3
        weight 0.4
    ]
    edge [
        source 4
        target 3
        weight 0.3
    ]
    edge [
        source 5
        target 3
        weight 0.2
    ]
    edge [
        source 0
        target 5
        weight 0.1
    ]
    edge [
        source 1
        target 5
        weight 0.9
    ]
]