<?php

require 'vendor/autoload.php';
$config = require 'app/config/config.php';
$pdo = new PDO('mysql:host=127.0.0.1;dbname=' . $config['database']['dbname'], $config['database']['user'], $config['database']['password']);

$shardPath = 'app/config/content/formulas/6c/shard_6c.json';
$shard = json_decode(file_get_contents($shardPath), true);
$f = &$shard['canonical-symplectic-2-form-local-representation-a888626a'];

$f['semantic_variables'] = [
    '\\omega' => [
        'name' => 'Canonical Symplectic 2-Form',
        'type' => 'variable',
        'unit' => 'J · s',
        'description' => 'The closed, non-degenerate differential 2-form on phase space defining Hamiltonian vector fields and Poisson brackets.'
    ],
    'dq_i' => [
        'name' => 'Coordinate Differential 1-Form',
        'type' => 'variable',
        'unit' => 'm or rad',
        'description' => 'Exterior derivative differential 1-form of the generalized position coordinate.'
    ],
    'dp_i' => [
        'name' => 'Momentum Differential 1-Form',
        'type' => 'variable',
        'unit' => 'kg · m/s or J · s',
        'description' => 'Exterior derivative differential 1-form of the conjugate momentum coordinate.'
    ],
    '\\wedge' => [
        'name' => 'Wedge Product (Exterior Product)',
        'type' => 'operator',
        'unit' => 'dimensionless',
        'description' => 'Antisymmetric exterior product of differential forms satisfying $dq_i \\wedge dp_i = -dp_i \\wedge dq_i$.'
    ],
    'n' => [
        'name' => 'Degrees of Freedom',
        'type' => 'variable',
        'unit' => 'dimensionless',
        'description' => 'Total number of mechanical degrees of freedom spanning the $2n$-dimensional phase space cotangent bundle $T^*Q$.'
    ],
    'i' => [
        'name' => 'Coordinate Index',
        'type' => 'variable',
        'unit' => 'dimensionless',
        'description' => 'Discrete summation index ranging from 1 to $n$ over each canonical coordinate-momentum pair.'
    ]
];

$f['interpretation'] = 'This equation provides the canonical local representation of the symplectic 2-form in terms of Darboux coordinates $(q_i, p_i)$. Each term $dq_i \\wedge dp_i$ represents an infinitesimal oriented area element in the 2-dimensional $(q_i, p_i)$ sub-plane of the phase space. Summing over all $n$ degrees of freedom yields the total symplectic structure on the $2n$-dimensional cotangent bundle $T^*Q$. Under time evolution governed by Hamilton\'s equations, the symplectic 2-form is preserved ($d\\omega/dt = 0$), which underlies Liouville\'s theorem stating that phase space volume is strictly conserved.';

$f['limits_and_boundary'] = 'This formulation is valid in classical Hamiltonian mechanics on smooth cotangent bundles where Darboux coordinates $(q_i, p_i)$ can be locally defined. By Darboux\'s theorem, any symplectic manifold locally admits coordinates where $\\omega$ takes this standard constant-coefficient canonical form. In the quantum transition, the exterior algebra on differential forms is replaced by the commutator algebra of non-commuting quantum operators via canonical quantization $[\\hat{q}_i, \\hat{p}_j] = i\\hbar \\delta_{ij}$.';

file_put_contents($shardPath, json_encode($shard, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE));

$stmt = $pdo->prepare('UPDATE formulas SET 
    semantic_variables = ?,
    interpretation = ?,
    limits_and_boundary = ?,
    equation_svg = NULL
    WHERE id = ?');

$stmt->execute([
    json_encode($f['semantic_variables'], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE),
    $f['interpretation'],
    $f['limits_and_boundary'],
    'canonical-symplectic-2-form-local-representation-a888626a'
]);

echo '[OK] Updated canonical symplectic 2-form definition and synced MariaDB.' . PHP_EOL;
