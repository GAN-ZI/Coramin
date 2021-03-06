import pyomo.environ as pe
import coramin
import unittest
from pyomo.core.expr.calculus.diff_with_pyomo import reverse_sd
from pyomo.core.expr.visitor import identify_variables, identify_components
import math
from pyomo.core.kernel.component_set import ComponentSet
import numpy as np
from pyomo.core.base.param import _ParamData, SimpleParam


class TestAutoRelax(unittest.TestCase):
    def test_product1(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(-1,1))
        m.y = pe.Var(bounds=(-1,1))
        m.z = pe.Var()
        m.c = pe.Constraint(expr=m.z - m.x*m.y == 0)

        rel = coramin.relaxations.relax(m)

        self.assertTrue(hasattr(rel, 'aux_cons'))
        self.assertTrue(hasattr(rel, 'aux_vars'))
        self.assertEqual(len(rel.aux_cons), 1)
        self.assertEqual(len(rel.aux_vars), 1)
        self.assertAlmostEqual(rel.aux_vars[1].lb, -1)
        self.assertAlmostEqual(rel.aux_vars[1].ub, 1)
        self.assertEqual(rel.aux_cons[1].lower, 0)
        self.assertEqual(rel.aux_cons[1].upper, 0)
        ders = reverse_sd(rel.aux_cons[1].body)
        self.assertEqual(ders[rel.z], 1)
        self.assertEqual(ders[rel.aux_vars[1]], -1)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[1].body))), 2)

        self.assertTrue(hasattr(rel, 'relaxations'))
        self.assertTrue(hasattr(rel.relaxations, 'rel0'))
        self.assertTrue(isinstance(rel.relaxations.rel0, coramin.relaxations.PWMcCormickRelaxation))
        self.assertIn(rel.x, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertIn(rel.y, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[1]), id(rel.relaxations.rel0.get_aux_var()))

    def test_product2(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(-1,1))
        m.y = pe.Var(bounds=(-1,1))
        m.z = pe.Var()
        m.v = pe.Var()
        m.c1 = pe.Constraint(expr=m.z - m.x*m.y == 0)
        m.c2 = pe.Constraint(expr=m.v - 3*m.x*m.y == 0)

        rel = coramin.relaxations.relax(m)

        self.assertTrue(hasattr(rel, 'aux_cons'))
        self.assertTrue(hasattr(rel, 'aux_vars'))
        self.assertEqual(len(rel.aux_cons), 2)
        self.assertEqual(len(rel.aux_vars), 1)
        self.assertAlmostEqual(rel.aux_vars[1].lb, -1)
        self.assertAlmostEqual(rel.aux_vars[1].ub, 1)

        self.assertEqual(rel.aux_cons[1].lower, 0)
        self.assertEqual(rel.aux_cons[1].upper, 0)
        ders = reverse_sd(rel.aux_cons[1].body)
        self.assertEqual(ders[rel.z], 1)
        self.assertEqual(ders[rel.aux_vars[1]], -1)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[1].body))), 2)

        self.assertEqual(rel.aux_cons[2].lower, 0)
        self.assertEqual(rel.aux_cons[2].upper, 0)
        ders = reverse_sd(rel.aux_cons[2].body)
        self.assertEqual(ders[rel.v], 1)
        self.assertEqual(ders[rel.aux_vars[1]], -3)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[2].body))), 2)

        self.assertTrue(hasattr(rel, 'relaxations'))
        self.assertTrue(hasattr(rel.relaxations, 'rel0'))
        self.assertTrue(isinstance(rel.relaxations.rel0, coramin.relaxations.PWMcCormickRelaxation))
        self.assertIn(rel.x, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertIn(rel.y, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[1]), id(rel.relaxations.rel0.get_aux_var()))

    def test_product3(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(-1,1))
        m.y = pe.Var(bounds=(-1,1))
        m.z = pe.Var()
        m.c = pe.Constraint(expr=m.z - m.x*m.y*3 == 0)

        rel = coramin.relaxations.relax(m)

        self.assertTrue(hasattr(rel, 'aux_cons'))
        self.assertTrue(hasattr(rel, 'aux_vars'))
        self.assertEqual(len(rel.aux_cons), 1)
        self.assertEqual(len(rel.aux_vars), 1)
        self.assertAlmostEqual(rel.aux_vars[1].lb, -1)
        self.assertAlmostEqual(rel.aux_vars[1].ub, 1)
        self.assertEqual(rel.aux_cons[1].lower, 0)
        self.assertEqual(rel.aux_cons[1].upper, 0)
        ders = reverse_sd(rel.aux_cons[1].body)
        self.assertEqual(ders[rel.z], 1)
        self.assertEqual(ders[rel.aux_vars[1]], -3)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[1].body))), 2)

        self.assertTrue(hasattr(rel, 'relaxations'))
        self.assertTrue(hasattr(rel.relaxations, 'rel0'))
        self.assertTrue(isinstance(rel.relaxations.rel0, coramin.relaxations.PWMcCormickRelaxation))
        self.assertIn(rel.x, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertIn(rel.y, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[1]), id(rel.relaxations.rel0.get_aux_var()))
        relaxations = list(coramin.relaxations.relaxation_data_objects(rel))
        self.assertEqual(len(relaxations), 1)

    def test_product4(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(-1,1))
        m.z = pe.Var()
        m.c = pe.Constraint(expr=m.z - m.x*m.x == 0)

        rel = coramin.relaxations.relax(m)

        self.assertTrue(hasattr(rel, 'aux_cons'))
        self.assertTrue(hasattr(rel, 'aux_vars'))
        self.assertEqual(len(rel.aux_cons), 1)
        self.assertEqual(len(rel.aux_vars), 1)
        self.assertAlmostEqual(rel.aux_vars[1].lb, 0)
        self.assertAlmostEqual(rel.aux_vars[1].ub, 1)
        self.assertEqual(rel.aux_cons[1].lower, 0)
        self.assertEqual(rel.aux_cons[1].upper, 0)
        ders = reverse_sd(rel.aux_cons[1].body)
        self.assertEqual(ders[rel.z], 1)
        self.assertEqual(ders[rel.aux_vars[1]], -1)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[1].body))), 2)

        self.assertTrue(hasattr(rel, 'relaxations'))
        self.assertTrue(hasattr(rel.relaxations, 'rel0'))
        self.assertTrue(isinstance(rel.relaxations.rel0, coramin.relaxations.PWXSquaredRelaxationData))
        self.assertIn(rel.x, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertEqual(len(rel.relaxations.rel0.get_rhs_vars()), 1)
        self.assertEqual(id(rel.aux_vars[1]), id(rel.relaxations.rel0.get_aux_var()))
        relaxations = list(coramin.relaxations.relaxation_data_objects(rel))
        self.assertEqual(len(relaxations), 1)

    def test_quadratic(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(-1,1))
        m.y = pe.Var()
        m.z = pe.Var()
        m.w = pe.Var()
        m.c = pe.Constraint(expr=m.x**2 + m.y + m.z == 0)
        m.c2 = pe.Constraint(expr=m.w - 3*m.x**2 == 0)

        rel = coramin.relaxations.relax(m)

        self.assertTrue(hasattr(rel, 'aux_cons'))
        self.assertTrue(hasattr(rel, 'aux_vars'))
        self.assertEqual(len(rel.aux_cons), 2)
        self.assertEqual(len(rel.aux_vars), 1)
        self.assertAlmostEqual(rel.aux_vars[1].lb, 0)
        self.assertAlmostEqual(rel.aux_vars[1].ub, 1)

        self.assertEqual(rel.aux_cons[1].lower, 0)
        self.assertEqual(rel.aux_cons[1].upper, 0)
        ders = reverse_sd(rel.aux_cons[1].body)
        self.assertEqual(ders[rel.z], 1)
        self.assertEqual(ders[rel.aux_vars[1]], 1)
        self.assertEqual(ders[rel.y], 1)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[1].body))), 3)

        self.assertEqual(rel.aux_cons[2].lower, 0)
        self.assertEqual(rel.aux_cons[2].upper, 0)
        ders = reverse_sd(rel.aux_cons[2].body)
        self.assertEqual(ders[rel.w], 1)
        self.assertEqual(ders[rel.aux_vars[1]], -3)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[2].body))), 2)

        self.assertTrue(hasattr(rel, 'relaxations'))
        self.assertTrue(hasattr(rel.relaxations, 'rel0'))
        self.assertTrue(isinstance(rel.relaxations.rel0, coramin.relaxations.PWXSquaredRelaxation))
        self.assertIn(rel.x, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[1]), id(rel.relaxations.rel0.get_aux_var()))
        self.assertFalse(hasattr(rel.relaxations, 'rel1'))

    def test_cubic_convex(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(1,2))
        m.y = pe.Var()
        m.z = pe.Var()
        m.w = pe.Var()
        m.c = pe.Constraint(expr=m.x**3 + m.y + m.z == 0)
        m.c2 = pe.Constraint(expr=m.w - 3*m.x**3 == 0)

        rel = coramin.relaxations.relax(m)

        self.assertTrue(hasattr(rel, 'aux_cons'))
        self.assertTrue(hasattr(rel, 'aux_vars'))
        self.assertEqual(len(rel.aux_cons), 2)
        self.assertEqual(len(rel.aux_vars), 1)
        self.assertAlmostEqual(rel.aux_vars[1].lb, 1)
        self.assertAlmostEqual(rel.aux_vars[1].ub, 8)

        self.assertEqual(rel.aux_cons[1].lower, 0)
        self.assertEqual(rel.aux_cons[1].upper, 0)
        ders = reverse_sd(rel.aux_cons[1].body)
        self.assertEqual(ders[rel.z], 1)
        self.assertEqual(ders[rel.aux_vars[1]], 1)
        self.assertEqual(ders[rel.y], 1)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[1].body))), 3)

        self.assertEqual(rel.aux_cons[2].lower, 0)
        self.assertEqual(rel.aux_cons[2].upper, 0)
        ders = reverse_sd(rel.aux_cons[2].body)
        self.assertEqual(ders[rel.w], 1)
        self.assertEqual(ders[rel.aux_vars[1]], -3)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[2].body))), 2)

        self.assertTrue(hasattr(rel, 'relaxations'))
        self.assertTrue(hasattr(rel.relaxations, 'rel0'))
        self.assertTrue(isinstance(rel.relaxations.rel0, coramin.relaxations.PWUnivariateRelaxation))
        self.assertIn(rel.x, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[1]), id(rel.relaxations.rel0.get_aux_var()))
        self.assertTrue(rel.relaxations.rel0.is_rhs_convex())
        self.assertFalse(rel.relaxations.rel0.is_rhs_concave())
        self.assertFalse(hasattr(rel.relaxations, 'rel1'))

    def test_cubic_concave(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(-2,-1))
        m.y = pe.Var()
        m.z = pe.Var()
        m.w = pe.Var()
        m.c = pe.Constraint(expr=m.x**3 + m.y + m.z == 0)
        m.c2 = pe.Constraint(expr=m.w - 3*m.x**3 == 0)

        rel = coramin.relaxations.relax(m)

        self.assertTrue(hasattr(rel, 'aux_cons'))
        self.assertTrue(hasattr(rel, 'aux_vars'))
        self.assertEqual(len(rel.aux_cons), 2)
        self.assertEqual(len(rel.aux_vars), 1)
        self.assertAlmostEqual(rel.aux_vars[1].lb, -8)
        self.assertAlmostEqual(rel.aux_vars[1].ub, -1)

        self.assertEqual(rel.aux_cons[1].lower, 0)
        self.assertEqual(rel.aux_cons[1].upper, 0)
        ders = reverse_sd(rel.aux_cons[1].body)
        self.assertEqual(ders[rel.z], 1)
        self.assertEqual(ders[rel.aux_vars[1]], 1)
        self.assertEqual(ders[rel.y], 1)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[1].body))), 3)

        self.assertEqual(rel.aux_cons[2].lower, 0)
        self.assertEqual(rel.aux_cons[2].upper, 0)
        ders = reverse_sd(rel.aux_cons[2].body)
        self.assertEqual(ders[rel.w], 1)
        self.assertEqual(ders[rel.aux_vars[1]], -3)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[2].body))), 2)

        self.assertTrue(hasattr(rel, 'relaxations'))
        self.assertTrue(hasattr(rel.relaxations, 'rel0'))
        self.assertTrue(isinstance(rel.relaxations.rel0, coramin.relaxations.PWUnivariateRelaxation))
        self.assertIn(rel.x, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[1]), id(rel.relaxations.rel0.get_aux_var()))
        self.assertFalse(rel.relaxations.rel0.is_rhs_convex())
        self.assertTrue(rel.relaxations.rel0.is_rhs_concave())
        self.assertFalse(hasattr(rel.relaxations, 'rel1'))

    def test_cubic(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(-1,1))
        m.y = pe.Var()
        m.z = pe.Var()
        m.w = pe.Var()
        m.c = pe.Constraint(expr=m.x**3 + m.y + m.z == 0)
        m.c2 = pe.Constraint(expr=m.w - 3*m.x**3 == 0)

        rel = coramin.relaxations.relax(m)

        # this problem should turn into
        #
        # aux2 + y + z = 0        => aux_con[1]
        # w - 3*aux2 = 0          => aux_con[2]
        # aux1 = x**2             => rel0
        # aux2 = x*aux1           => rel1

        self.assertTrue(hasattr(rel, 'aux_cons'))
        self.assertTrue(hasattr(rel, 'aux_vars'))
        self.assertEqual(len(rel.aux_cons), 2)
        self.assertEqual(len(rel.aux_vars), 2)

        self.assertAlmostEqual(rel.aux_vars[1].lb, 0)
        self.assertAlmostEqual(rel.aux_vars[1].ub, 1)

        self.assertAlmostEqual(rel.aux_vars[2].lb, -1)
        self.assertAlmostEqual(rel.aux_vars[2].ub, 1)

        self.assertEqual(rel.aux_cons[1].lower, 0)
        self.assertEqual(rel.aux_cons[1].upper, 0)
        ders = reverse_sd(rel.aux_cons[1].body)
        self.assertEqual(ders[rel.z], 1)
        self.assertEqual(ders[rel.aux_vars[2]], 1)
        self.assertEqual(ders[rel.y], 1)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[1].body))), 3)

        self.assertEqual(rel.aux_cons[2].lower, 0)
        self.assertEqual(rel.aux_cons[2].upper, 0)
        ders = reverse_sd(rel.aux_cons[2].body)
        self.assertEqual(ders[rel.w], 1)
        self.assertEqual(ders[rel.aux_vars[2]], -3)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[2].body))), 2)

        self.assertTrue(hasattr(rel, 'relaxations'))
        self.assertTrue(hasattr(rel.relaxations, 'rel0'))
        self.assertTrue(isinstance(rel.relaxations.rel0, coramin.relaxations.PWXSquaredRelaxation))
        self.assertIn(rel.x, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[1]), id(rel.relaxations.rel0.get_aux_var()))

        self.assertTrue(hasattr(rel.relaxations, 'rel1'))
        self.assertTrue(isinstance(rel.relaxations.rel1, coramin.relaxations.PWMcCormickRelaxation))
        self.assertIn(rel.x, ComponentSet(rel.relaxations.rel1.get_rhs_vars()))
        self.assertIn(rel.aux_vars[1], ComponentSet(rel.relaxations.rel1.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[2]), id(rel.relaxations.rel1.get_aux_var()))

    def test_pow_fractional1(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(-1,1))
        m.y = pe.Var()
        m.z = pe.Var()
        m.w = pe.Var()
        m.p = pe.Param(initialize=0.5)
        m.c = pe.Constraint(expr=m.x**m.p + m.y + m.z == 0)
        m.c2 = pe.Constraint(expr=m.w - 3*m.x**m.p == 0)

        rel = coramin.relaxations.relax(m)

        self.assertTrue(hasattr(rel, 'aux_cons'))
        self.assertTrue(hasattr(rel, 'aux_vars'))
        self.assertEqual(len(rel.aux_cons), 2)
        self.assertEqual(len(rel.aux_vars), 1)
        self.assertAlmostEqual(rel.aux_vars[1].lb, 0)
        self.assertAlmostEqual(rel.aux_vars[1].ub, 1)

        self.assertEqual(rel.aux_cons[1].lower, 0)
        self.assertEqual(rel.aux_cons[1].upper, 0)
        ders = reverse_sd(rel.aux_cons[1].body)
        self.assertEqual(ders[rel.z], 1)
        self.assertEqual(ders[rel.aux_vars[1]], 1)
        self.assertEqual(ders[rel.y], 1)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[1].body))), 3)

        self.assertEqual(rel.aux_cons[2].lower, 0)
        self.assertEqual(rel.aux_cons[2].upper, 0)
        ders = reverse_sd(rel.aux_cons[2].body)
        self.assertEqual(ders[rel.w], 1)
        self.assertEqual(ders[rel.aux_vars[1]], -3)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[2].body))), 2)

        self.assertTrue(hasattr(rel, 'relaxations'))
        self.assertTrue(hasattr(rel.relaxations, 'rel0'))
        self.assertTrue(isinstance(rel.relaxations.rel0, coramin.relaxations.PWUnivariateRelaxation))
        self.assertIn(rel.x, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[1]), id(rel.relaxations.rel0.get_aux_var()))
        self.assertFalse(rel.relaxations.rel0.is_rhs_convex())
        self.assertTrue(rel.relaxations.rel0.is_rhs_concave())
        self.assertFalse(hasattr(rel.relaxations, 'rel1'))

    def test_pow_fractional2(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(-1,1))
        m.y = pe.Var()
        m.z = pe.Var()
        m.w = pe.Var()
        m.p = pe.Param(initialize=1.5)
        m.c = pe.Constraint(expr=m.x**m.p + m.y + m.z == 0)
        m.c2 = pe.Constraint(expr=m.w - 3*m.x**m.p == 0)

        rel = coramin.relaxations.relax(m)

        self.assertTrue(hasattr(rel, 'aux_cons'))
        self.assertTrue(hasattr(rel, 'aux_vars'))
        self.assertEqual(len(rel.aux_cons), 2)
        self.assertEqual(len(rel.aux_vars), 1)
        self.assertAlmostEqual(rel.aux_vars[1].lb, 0)
        self.assertAlmostEqual(rel.aux_vars[1].ub, 1)

        self.assertEqual(rel.aux_cons[1].lower, 0)
        self.assertEqual(rel.aux_cons[1].upper, 0)
        ders = reverse_sd(rel.aux_cons[1].body)
        self.assertEqual(ders[rel.z], 1)
        self.assertEqual(ders[rel.aux_vars[1]], 1)
        self.assertEqual(ders[rel.y], 1)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[1].body))), 3)

        self.assertEqual(rel.aux_cons[2].lower, 0)
        self.assertEqual(rel.aux_cons[2].upper, 0)
        ders = reverse_sd(rel.aux_cons[2].body)
        self.assertEqual(ders[rel.w], 1)
        self.assertEqual(ders[rel.aux_vars[1]], -3)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[2].body))), 2)

        self.assertTrue(hasattr(rel, 'relaxations'))
        self.assertTrue(hasattr(rel.relaxations, 'rel0'))
        self.assertTrue(isinstance(rel.relaxations.rel0, coramin.relaxations.PWUnivariateRelaxation))
        self.assertIn(rel.x, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[1]), id(rel.relaxations.rel0.get_aux_var()))
        self.assertTrue(rel.relaxations.rel0.is_rhs_convex())
        self.assertFalse(rel.relaxations.rel0.is_rhs_concave())
        self.assertFalse(hasattr(rel.relaxations, 'rel1'))

    def test_pow_neg_even1(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(1,2))
        m.y = pe.Var()
        m.z = pe.Var()
        m.w = pe.Var()
        m.p = pe.Param(initialize=-2)
        m.c = pe.Constraint(expr=m.x**m.p + m.y + m.z == 0)
        m.c2 = pe.Constraint(expr=m.w - 3*m.x**m.p == 0)

        rel = coramin.relaxations.relax(m)

        self.assertTrue(hasattr(rel, 'aux_cons'))
        self.assertTrue(hasattr(rel, 'aux_vars'))
        self.assertEqual(len(rel.aux_cons), 2)
        self.assertEqual(len(rel.aux_vars), 1)
        self.assertAlmostEqual(rel.aux_vars[1].lb, 0.25)
        self.assertAlmostEqual(rel.aux_vars[1].ub, 1)

        self.assertEqual(rel.aux_cons[1].lower, 0)
        self.assertEqual(rel.aux_cons[1].upper, 0)
        ders = reverse_sd(rel.aux_cons[1].body)
        self.assertEqual(ders[rel.z], 1)
        self.assertEqual(ders[rel.aux_vars[1]], 1)
        self.assertEqual(ders[rel.y], 1)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[1].body))), 3)

        self.assertEqual(rel.aux_cons[2].lower, 0)
        self.assertEqual(rel.aux_cons[2].upper, 0)
        ders = reverse_sd(rel.aux_cons[2].body)
        self.assertEqual(ders[rel.w], 1)
        self.assertEqual(ders[rel.aux_vars[1]], -3)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[2].body))), 2)

        self.assertTrue(hasattr(rel, 'relaxations'))
        self.assertTrue(hasattr(rel.relaxations, 'rel0'))
        self.assertTrue(isinstance(rel.relaxations.rel0, coramin.relaxations.PWUnivariateRelaxation))
        self.assertIn(rel.x, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[1]), id(rel.relaxations.rel0.get_aux_var()))
        self.assertTrue(rel.relaxations.rel0.is_rhs_convex())
        self.assertFalse(rel.relaxations.rel0.is_rhs_concave())
        self.assertFalse(hasattr(rel.relaxations, 'rel1'))

    def test_pow_neg_even2(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(-2,-1))
        m.y = pe.Var()
        m.z = pe.Var()
        m.w = pe.Var()
        m.p = pe.Param(initialize=-2)
        m.c = pe.Constraint(expr=m.x**m.p + m.y + m.z == 0)
        m.c2 = pe.Constraint(expr=m.w - 3*m.x**m.p == 0)

        rel = coramin.relaxations.relax(m)

        self.assertTrue(hasattr(rel, 'aux_cons'))
        self.assertTrue(hasattr(rel, 'aux_vars'))
        self.assertEqual(len(rel.aux_cons), 2)
        self.assertEqual(len(rel.aux_vars), 1)
        self.assertAlmostEqual(rel.aux_vars[1].lb, 0.25)
        self.assertAlmostEqual(rel.aux_vars[1].ub, 1)

        self.assertEqual(rel.aux_cons[1].lower, 0)
        self.assertEqual(rel.aux_cons[1].upper, 0)
        ders = reverse_sd(rel.aux_cons[1].body)
        self.assertEqual(ders[rel.z], 1)
        self.assertEqual(ders[rel.aux_vars[1]], 1)
        self.assertEqual(ders[rel.y], 1)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[1].body))), 3)

        self.assertEqual(rel.aux_cons[2].lower, 0)
        self.assertEqual(rel.aux_cons[2].upper, 0)
        ders = reverse_sd(rel.aux_cons[2].body)
        self.assertEqual(ders[rel.w], 1)
        self.assertEqual(ders[rel.aux_vars[1]], -3)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[2].body))), 2)

        self.assertTrue(hasattr(rel, 'relaxations'))
        self.assertTrue(hasattr(rel.relaxations, 'rel0'))
        self.assertTrue(isinstance(rel.relaxations.rel0, coramin.relaxations.PWUnivariateRelaxation))
        self.assertIn(rel.x, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[1]), id(rel.relaxations.rel0.get_aux_var()))
        self.assertTrue(rel.relaxations.rel0.is_rhs_convex())
        self.assertFalse(rel.relaxations.rel0.is_rhs_concave())
        self.assertFalse(hasattr(rel.relaxations, 'rel1'))

    def test_pow_neg_odd1(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(1,2))
        m.y = pe.Var()
        m.z = pe.Var()
        m.w = pe.Var()
        m.p = pe.Param(initialize=-3)
        m.c = pe.Constraint(expr=m.x**m.p + m.y + m.z == 0)
        m.c2 = pe.Constraint(expr=m.w - 3*m.x**m.p == 0)

        rel = coramin.relaxations.relax(m)

        self.assertTrue(hasattr(rel, 'aux_cons'))
        self.assertTrue(hasattr(rel, 'aux_vars'))
        self.assertEqual(len(rel.aux_cons), 2)
        self.assertEqual(len(rel.aux_vars), 1)
        self.assertAlmostEqual(rel.aux_vars[1].lb, 0.125)
        self.assertAlmostEqual(rel.aux_vars[1].ub, 1)

        self.assertEqual(rel.aux_cons[1].lower, 0)
        self.assertEqual(rel.aux_cons[1].upper, 0)
        ders = reverse_sd(rel.aux_cons[1].body)
        self.assertEqual(ders[rel.z], 1)
        self.assertEqual(ders[rel.aux_vars[1]], 1)
        self.assertEqual(ders[rel.y], 1)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[1].body))), 3)

        self.assertEqual(rel.aux_cons[2].lower, 0)
        self.assertEqual(rel.aux_cons[2].upper, 0)
        ders = reverse_sd(rel.aux_cons[2].body)
        self.assertEqual(ders[rel.w], 1)
        self.assertEqual(ders[rel.aux_vars[1]], -3)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[2].body))), 2)

        self.assertTrue(hasattr(rel, 'relaxations'))
        self.assertTrue(hasattr(rel.relaxations, 'rel0'))
        self.assertTrue(isinstance(rel.relaxations.rel0, coramin.relaxations.PWUnivariateRelaxation))
        self.assertIn(rel.x, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[1]), id(rel.relaxations.rel0.get_aux_var()))
        self.assertTrue(rel.relaxations.rel0.is_rhs_convex())
        self.assertFalse(rel.relaxations.rel0.is_rhs_concave())
        self.assertFalse(hasattr(rel.relaxations, 'rel1'))

    def test_pow_neg_odd2(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(-2,-1))
        m.y = pe.Var()
        m.z = pe.Var()
        m.w = pe.Var()
        m.p = pe.Param(initialize=-3)
        m.c = pe.Constraint(expr=m.x**m.p + m.y + m.z == 0)
        m.c2 = pe.Constraint(expr=m.w - 3*m.x**m.p == 0)

        rel = coramin.relaxations.relax(m)

        self.assertTrue(hasattr(rel, 'aux_cons'))
        self.assertTrue(hasattr(rel, 'aux_vars'))
        self.assertEqual(len(rel.aux_cons), 2)
        self.assertEqual(len(rel.aux_vars), 1)
        self.assertAlmostEqual(rel.aux_vars[1].lb, -1)
        self.assertAlmostEqual(rel.aux_vars[1].ub, -0.125)

        self.assertEqual(rel.aux_cons[1].lower, 0)
        self.assertEqual(rel.aux_cons[1].upper, 0)
        ders = reverse_sd(rel.aux_cons[1].body)
        self.assertEqual(ders[rel.z], 1)
        self.assertEqual(ders[rel.aux_vars[1]], 1)
        self.assertEqual(ders[rel.y], 1)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[1].body))), 3)

        self.assertEqual(rel.aux_cons[2].lower, 0)
        self.assertEqual(rel.aux_cons[2].upper, 0)
        ders = reverse_sd(rel.aux_cons[2].body)
        self.assertEqual(ders[rel.w], 1)
        self.assertEqual(ders[rel.aux_vars[1]], -3)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[2].body))), 2)

        self.assertTrue(hasattr(rel, 'relaxations'))
        self.assertTrue(hasattr(rel.relaxations, 'rel0'))
        self.assertTrue(isinstance(rel.relaxations.rel0, coramin.relaxations.PWUnivariateRelaxation))
        self.assertIn(rel.x, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[1]), id(rel.relaxations.rel0.get_aux_var()))
        self.assertFalse(rel.relaxations.rel0.is_rhs_convex())
        self.assertTrue(rel.relaxations.rel0.is_rhs_concave())
        self.assertFalse(hasattr(rel.relaxations, 'rel1'))

    def test_pow_neg(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(-1,1))
        m.y = pe.Var()
        m.z = pe.Var()
        m.w = pe.Var()
        m.p = pe.Param(initialize=-2)
        m.c = pe.Constraint(expr=m.x**m.p + m.y + m.z == 0)
        m.c2 = pe.Constraint(expr=m.w - 3*m.x**m.p == 0)

        rel = coramin.relaxations.relax(m)

        # This model should be relaxed to
        #
        # aux2 + y + z = 0
        # w - 3 * aux2 = 0
        # aux1 = x**2
        # aux1*aux2 = aux3
        # aux3 = 1
        #

        self.assertTrue(hasattr(rel, 'aux_cons'))
        self.assertTrue(hasattr(rel, 'aux_vars'))
        self.assertEqual(len(rel.aux_cons), 2)
        self.assertEqual(len(rel.aux_vars), 3)

        self.assertAlmostEqual(rel.aux_vars[1].lb, 0)
        self.assertAlmostEqual(rel.aux_vars[1].ub, 1)

        self.assertTrue(rel.aux_vars[3].is_fixed())
        self.assertEqual(rel.aux_vars[3].value, 1)

        self.assertEqual(rel.aux_cons[1].lower, 0)
        self.assertEqual(rel.aux_cons[1].upper, 0)
        ders = reverse_sd(rel.aux_cons[1].body)
        self.assertEqual(ders[rel.z], 1)
        self.assertEqual(ders[rel.aux_vars[2]], 1)
        self.assertEqual(ders[rel.y], 1)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[1].body))), 3)

        self.assertEqual(rel.aux_cons[2].lower, 0)
        self.assertEqual(rel.aux_cons[2].upper, 0)
        ders = reverse_sd(rel.aux_cons[2].body)
        self.assertEqual(ders[rel.w], 1)
        self.assertEqual(ders[rel.aux_vars[2]], -3)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[2].body))), 2)

        self.assertTrue(hasattr(rel, 'relaxations'))
        self.assertTrue(hasattr(rel.relaxations, 'rel0'))
        self.assertTrue(isinstance(rel.relaxations.rel0, coramin.relaxations.PWXSquaredRelaxation))
        self.assertIn(rel.x, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[1]), id(rel.relaxations.rel0.get_aux_var()))
        self.assertTrue(rel.relaxations.rel0.is_rhs_convex())
        self.assertFalse(rel.relaxations.rel0.is_rhs_concave())

        self.assertTrue(hasattr(rel.relaxations, 'rel1'))
        self.assertTrue(isinstance(rel.relaxations.rel1, coramin.relaxations.PWMcCormickRelaxation))
        self.assertIn(rel.aux_vars[1], ComponentSet(rel.relaxations.rel1.get_rhs_vars()))
        self.assertIn(rel.aux_vars[2], ComponentSet(rel.relaxations.rel1.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[3]), id(rel.relaxations.rel1.get_aux_var()))

        self.assertFalse(hasattr(rel.relaxations, 'rel2'))

    def test_exp(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(-1,1))
        m.y = pe.Var(bounds=(-1,1))
        m.z = pe.Var()
        m.w = pe.Var()
        m.c = pe.Constraint(expr=pe.exp(m.x*m.y) + m.z == 0)
        m.c2 = pe.Constraint(expr=m.w - 3*pe.exp(m.x*m.y) == 0)

        rel = coramin.relaxations.relax(m)

        self.assertTrue(hasattr(rel, 'aux_cons'))
        self.assertTrue(hasattr(rel, 'aux_vars'))
        self.assertEqual(len(rel.aux_cons), 2)
        self.assertEqual(len(rel.aux_vars), 2)

        self.assertAlmostEqual(rel.aux_vars[1].lb, -1)
        self.assertAlmostEqual(rel.aux_vars[1].ub, 1)

        self.assertAlmostEqual(rel.aux_vars[2].lb, math.exp(-1))
        self.assertAlmostEqual(rel.aux_vars[2].ub, math.exp(1))

        self.assertEqual(rel.aux_cons[1].lower, 0)
        self.assertEqual(rel.aux_cons[1].upper, 0)
        ders = reverse_sd(rel.aux_cons[1].body)
        self.assertEqual(ders[rel.z], 1)
        self.assertEqual(ders[rel.aux_vars[2]], 1)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[1].body))), 2)

        self.assertEqual(rel.aux_cons[2].lower, 0)
        self.assertEqual(rel.aux_cons[2].upper, 0)
        ders = reverse_sd(rel.aux_cons[2].body)
        self.assertEqual(ders[rel.w], 1)
        self.assertEqual(ders[rel.aux_vars[2]], -3)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[2].body))), 2)

        self.assertTrue(hasattr(rel, 'relaxations'))
        self.assertTrue(hasattr(rel.relaxations, 'rel0'))
        self.assertTrue(isinstance(rel.relaxations.rel0, coramin.relaxations.PWMcCormickRelaxation))
        self.assertIn(rel.x, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertIn(rel.y, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[1]), id(rel.relaxations.rel0.get_aux_var()))

        self.assertTrue(hasattr(rel.relaxations, 'rel1'))
        self.assertTrue(isinstance(rel.relaxations.rel1, coramin.relaxations.PWUnivariateRelaxation))
        self.assertEqual(id(rel.aux_vars[1]), id(rel.relaxations.rel1._x))
        self.assertEqual(id(rel.aux_vars[2]), id(rel.relaxations.rel1.get_aux_var()))
        self.assertTrue(rel.relaxations.rel1.is_rhs_convex())
        self.assertFalse(rel.relaxations.rel1.is_rhs_concave())

        self.assertFalse(hasattr(rel.relaxations, 'rel2'))

    def test_log(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(1,2))
        m.y = pe.Var(bounds=(1,2))
        m.z = pe.Var()
        m.w = pe.Var()
        m.c = pe.Constraint(expr=pe.log(m.x*m.y) + m.z == 0)
        m.c2 = pe.Constraint(expr=m.w - 3*pe.log(m.x*m.y) == 0)

        rel = coramin.relaxations.relax(m)

        self.assertTrue(hasattr(rel, 'aux_cons'))
        self.assertTrue(hasattr(rel, 'aux_vars'))
        self.assertEqual(len(rel.aux_cons), 2)
        self.assertEqual(len(rel.aux_vars), 2)

        self.assertAlmostEqual(rel.aux_vars[1].lb, 1)
        self.assertAlmostEqual(rel.aux_vars[1].ub, 4)

        self.assertAlmostEqual(rel.aux_vars[2].lb, math.log(1))
        self.assertAlmostEqual(rel.aux_vars[2].ub, math.log(4))

        self.assertEqual(rel.aux_cons[1].lower, 0)
        self.assertEqual(rel.aux_cons[1].upper, 0)
        ders = reverse_sd(rel.aux_cons[1].body)
        self.assertEqual(ders[rel.z], 1)
        self.assertEqual(ders[rel.aux_vars[2]], 1)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[1].body))), 2)

        self.assertEqual(rel.aux_cons[2].lower, 0)
        self.assertEqual(rel.aux_cons[2].upper, 0)
        ders = reverse_sd(rel.aux_cons[2].body)
        self.assertEqual(ders[rel.w], 1)
        self.assertEqual(ders[rel.aux_vars[2]], -3)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[2].body))), 2)

        self.assertTrue(hasattr(rel, 'relaxations'))
        self.assertTrue(hasattr(rel.relaxations, 'rel0'))
        self.assertTrue(isinstance(rel.relaxations.rel0, coramin.relaxations.PWMcCormickRelaxation))
        self.assertIn(rel.x, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertIn(rel.y, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[1]), id(rel.relaxations.rel0.get_aux_var()))

        self.assertTrue(hasattr(rel.relaxations, 'rel1'))
        self.assertTrue(isinstance(rel.relaxations.rel1, coramin.relaxations.PWUnivariateRelaxation))
        self.assertIn(rel.aux_vars[1], ComponentSet(rel.relaxations.rel1.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[2]), id(rel.relaxations.rel1.get_aux_var()))
        self.assertFalse(rel.relaxations.rel1.is_rhs_convex())
        self.assertTrue(rel.relaxations.rel1.is_rhs_concave())

        self.assertFalse(hasattr(rel.relaxations, 'rel2'))

    def test_div1(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(-1, 1))
        m.y = pe.Var(bounds=(1, 2))
        m.z = pe.Var()
        m.c = pe.Constraint(expr=m.z - m.x/m.y == 0)
        rel = coramin.relaxations.relax(m, in_place=True)
        self.assertIs(m, rel)
        relaxations = list(coramin.relaxations.relaxation_data_objects(m))
        constraints = list(coramin.relaxations.nonrelaxation_component_data_objects(m, ctype=pe.Constraint))
        vars = list(coramin.relaxations.nonrelaxation_component_data_objects(m, ctype=pe.Var))
        self.assertEqual(len(relaxations), 1)
        self.assertEqual(len(constraints), 1)
        self.assertEqual(len(vars), 4)
        r = relaxations[0]
        c = constraints[0]
        self.assertIsInstance(r, coramin.relaxations.PWMcCormickRelaxationData)
        c_vars = ComponentSet(identify_variables(c.body))
        self.assertEqual(len(c_vars), 2)
        self.assertEqual(len(rel.aux_vars), 1)
        self.assertIn(m.aux_vars[1], c_vars)
        self.assertIn(m.z, c_vars)
        r_vars = ComponentSet(r.get_rhs_vars())
        self.assertIn(m.y, r_vars)
        self.assertIn(m.aux_vars[1], r_vars)
        self.assertIs(r.get_aux_var(), m.x)

    def test_div2(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(-1,1))
        m.y = pe.Var(bounds=(-1,1))
        m.z = pe.Var()
        m.c = pe.Constraint(expr=m.z - m.x*m.y/2 == 0)

        rel = coramin.relaxations.relax(m)

        self.assertTrue(hasattr(rel, 'aux_cons'))
        self.assertTrue(hasattr(rel, 'aux_vars'))
        self.assertEqual(len(rel.aux_cons), 1)
        self.assertEqual(len(rel.aux_vars), 1)
        self.assertAlmostEqual(rel.aux_vars[1].lb, -1)
        self.assertAlmostEqual(rel.aux_vars[1].ub, 1)
        self.assertEqual(rel.aux_cons[1].lower, 0)
        self.assertEqual(rel.aux_cons[1].upper, 0)
        ders = reverse_sd(rel.aux_cons[1].body)
        self.assertEqual(ders[rel.z], 1)
        self.assertEqual(ders[rel.aux_vars[1]], -0.5)
        self.assertEqual(len(list(identify_variables(rel.aux_cons[1].body))), 2)

        self.assertTrue(hasattr(rel, 'relaxations'))
        self.assertTrue(hasattr(rel.relaxations, 'rel0'))
        self.assertTrue(isinstance(rel.relaxations.rel0, coramin.relaxations.PWMcCormickRelaxation))
        self.assertIn(rel.x, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertIn(rel.y, ComponentSet(rel.relaxations.rel0.get_rhs_vars()))
        self.assertEqual(id(rel.aux_vars[1]), id(rel.relaxations.rel0.get_aux_var()))
        relaxations = list(coramin.relaxations.relaxation_data_objects(rel))
        self.assertEqual(len(relaxations), 1)

    def test_div3(self):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(-1, 1))
        m.y = pe.Var(bounds=(1, 2))
        m.z = pe.Var()
        m.w = pe.Var()
        m.c = pe.Constraint(expr=m.z - m.x/m.y == 0)
        m.c2 = pe.Constraint(expr=m.w - m.x/m.y == 0)
        rel = coramin.relaxations.relax(m, in_place=True)
        self.assertIs(m, rel)
        relaxations = list(coramin.relaxations.relaxation_data_objects(m))
        constraints = list(coramin.relaxations.nonrelaxation_component_data_objects(m, ctype=pe.Constraint))
        vars = list(coramin.relaxations.nonrelaxation_component_data_objects(m, ctype=pe.Var))
        self.assertEqual(len(relaxations), 1)
        self.assertEqual(len(constraints), 2)
        self.assertEqual(len(vars), 5)
        r = relaxations[0]
        c1 = constraints[0]
        c2 = constraints[1]
        self.assertIsInstance(r, coramin.relaxations.PWMcCormickRelaxationData)
        c1_vars = ComponentSet(identify_variables(c1.body))
        c2_vars = ComponentSet(identify_variables(c2.body))
        self.assertEqual(len(c1_vars), 2)
        self.assertEqual(len(c2_vars), 2)
        self.assertEqual(len(rel.aux_vars), 1)
        self.assertIn(m.aux_vars[1], c1_vars)
        self.assertIn(m.aux_vars[1], c2_vars)
        self.assertTrue(m.z in c1_vars or m.z in c2_vars)
        self.assertTrue(m.w in c1_vars or m.w in c2_vars)
        r_vars = ComponentSet(r.get_rhs_vars())
        self.assertIn(m.y, r_vars)
        self.assertIn(m.aux_vars[1], r_vars)
        self.assertIs(r.get_aux_var(), m.x)


class TestUnivariate(unittest.TestCase):
    def helper(self, func, bounds_list, relaxation_side, expected_relaxation_side):
        for lb, ub in bounds_list:
            m = pe.ConcreteModel()
            m.x = pe.Var(bounds=(lb, ub))
            m.aux = pe.Var()
            if relaxation_side == coramin.utils.RelaxationSide.BOTH:
                m.c = pe.Constraint(expr=m.aux == func(m.x))
            elif relaxation_side == coramin.utils.RelaxationSide.UNDER:
                m.c = pe.Constraint(expr=m.aux >= func(m.x))
            elif relaxation_side == coramin.utils.RelaxationSide.OVER:
                m.c = pe.Constraint(expr=m.aux <= func(m.x))
            coramin.relaxations.relax(m, in_place=True)
            rels = list(coramin.relaxations.relaxation_data_objects(m))
            self.assertEqual(len(rels), 1)
            r = rels[0]
            self.assertEqual(r.relaxation_side, expected_relaxation_side)
            m.p = pe.Param(mutable=True, initialize=0)
            m.c2 = pe.Constraint(expr=m.x == m.p)
            opt = pe.SolverFactory('cplex_persistent')
            opt.set_instance(m)
            for _x in [float(i) for i in np.linspace(lb, ub, 10)]:
                m.p.value = _x
                opt.remove_constraint(m.c2)
                opt.add_constraint(m.c2)
                if relaxation_side in {coramin.utils.RelaxationSide.BOTH, coramin.utils.RelaxationSide.UNDER}:
                    m.obj = pe.Objective(expr=m.aux)
                    opt.set_objective(m.obj)
                    res = opt.solve()
                    self.assertEqual(res.solver.termination_condition, pe.TerminationCondition.optimal)
                    self.assertLessEqual(m.aux.value, func(_x) + 1e-10)
                    del m.obj
                if relaxation_side in {coramin.utils.RelaxationSide.BOTH, coramin.utils.RelaxationSide.OVER}:
                    m.obj = pe.Objective(expr=m.aux, sense=pe.maximize)
                    opt.set_objective(m.obj)
                    res = opt.solve()
                    self.assertEqual(res.solver.termination_condition, pe.TerminationCondition.optimal)
                    self.assertGreaterEqual(m.aux.value, func(_x) - 1e-10)
                    del m.obj

    def test_exp(self):
        self.helper(func=pe.exp,
                    bounds_list=[(-1, 1)],
                    relaxation_side=coramin.utils.RelaxationSide.BOTH,
                    expected_relaxation_side=coramin.utils.RelaxationSide.BOTH)
        self.helper(func=pe.exp,
                    bounds_list=[(-1, 1)],
                    relaxation_side=coramin.utils.RelaxationSide.UNDER,
                    expected_relaxation_side=coramin.utils.RelaxationSide.UNDER)
        self.helper(func=pe.exp,
                    bounds_list=[(-1, 1)],
                    relaxation_side=coramin.utils.RelaxationSide.OVER,
                    expected_relaxation_side=coramin.utils.RelaxationSide.OVER)

    def test_log(self):
        self.helper(func=pe.log,
                    bounds_list=[(0.5, 1.5)],
                    relaxation_side=coramin.utils.RelaxationSide.BOTH,
                    expected_relaxation_side=coramin.utils.RelaxationSide.BOTH)
        self.helper(func=pe.log,
                    bounds_list=[(0.5, 1.5)],
                    relaxation_side=coramin.utils.RelaxationSide.UNDER,
                    expected_relaxation_side=coramin.utils.RelaxationSide.UNDER)
        self.helper(func=pe.log,
                    bounds_list=[(0.5, 1.5)],
                    relaxation_side=coramin.utils.RelaxationSide.OVER,
                    expected_relaxation_side=coramin.utils.RelaxationSide.OVER)

    def test_log10(self):
        self.helper(func=pe.log10,
                    bounds_list=[(0.5, 1.5)],
                    relaxation_side=coramin.utils.RelaxationSide.BOTH,
                    expected_relaxation_side=coramin.utils.RelaxationSide.BOTH)
        self.helper(func=pe.log10,
                    bounds_list=[(0.5, 1.5)],
                    relaxation_side=coramin.utils.RelaxationSide.UNDER,
                    expected_relaxation_side=coramin.utils.RelaxationSide.UNDER)
        self.helper(func=pe.log10,
                    bounds_list=[(0.5, 1.5)],
                    relaxation_side=coramin.utils.RelaxationSide.OVER,
                    expected_relaxation_side=coramin.utils.RelaxationSide.OVER)

    def test_quadratic(self):
        def quadratic_func(x):
            return x**2
        self.helper(func=quadratic_func,
                    bounds_list=[(-1, 2)],
                    relaxation_side=coramin.utils.RelaxationSide.BOTH,
                    expected_relaxation_side=coramin.utils.RelaxationSide.BOTH)
        self.helper(func=quadratic_func,
                    bounds_list=[(-1, 2)],
                    relaxation_side=coramin.utils.RelaxationSide.UNDER,
                    expected_relaxation_side=coramin.utils.RelaxationSide.UNDER)
        self.helper(func=quadratic_func,
                    bounds_list=[(-1, 2)],
                    relaxation_side=coramin.utils.RelaxationSide.UNDER,
                    expected_relaxation_side=coramin.utils.RelaxationSide.UNDER)

    def test_arctan(self):
        self.helper(func=pe.atan,
                    bounds_list=[(-1, 1)],
                    relaxation_side=coramin.utils.RelaxationSide.BOTH,
                    expected_relaxation_side=coramin.utils.RelaxationSide.BOTH)
        self.helper(func=pe.atan,
                    bounds_list=[(-1, 1)],
                    relaxation_side=coramin.utils.RelaxationSide.UNDER,
                    expected_relaxation_side=coramin.utils.RelaxationSide.UNDER)
        self.helper(func=pe.atan,
                    bounds_list=[(-1, 1)],
                    relaxation_side=coramin.utils.RelaxationSide.OVER,
                    expected_relaxation_side=coramin.utils.RelaxationSide.OVER)

    def test_sin(self):
        self.helper(func=pe.sin,
                    bounds_list=[(-1, 1)],
                    relaxation_side=coramin.utils.RelaxationSide.BOTH,
                    expected_relaxation_side=coramin.utils.RelaxationSide.BOTH)
        self.helper(func=pe.sin,
                    bounds_list=[(-1, 1)],
                    relaxation_side=coramin.utils.RelaxationSide.UNDER,
                    expected_relaxation_side=coramin.utils.RelaxationSide.UNDER)
        self.helper(func=pe.sin,
                    bounds_list=[(-1, 1)],
                    relaxation_side=coramin.utils.RelaxationSide.OVER,
                    expected_relaxation_side=coramin.utils.RelaxationSide.OVER)

    def test_cos(self):
        self.helper(func=pe.cos,
                    bounds_list=[(-1, 1)],
                    relaxation_side=coramin.utils.RelaxationSide.BOTH,
                    expected_relaxation_side=coramin.utils.RelaxationSide.BOTH)
        self.helper(func=pe.cos,
                    bounds_list=[(-1, 1)],
                    relaxation_side=coramin.utils.RelaxationSide.UNDER,
                    expected_relaxation_side=coramin.utils.RelaxationSide.UNDER)
        self.helper(func=pe.cos,
                    bounds_list=[(-1, 1)],
                    relaxation_side=coramin.utils.RelaxationSide.OVER,
                    expected_relaxation_side=coramin.utils.RelaxationSide.OVER)


class TestRepeatedTerms(unittest.TestCase):
    def helper(self, func, lb, ub):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(lb, ub))
        m.aux1 = pe.Var()
        m.aux2 = pe.Var()
        m.c1 = pe.Constraint(expr=m.aux1 <= 2 * func(m.x) + 3)
        m.c2 = pe.Constraint(expr=m.aux2 >= 3 * func(m.x) + 2)
        coramin.relaxations.relax(m, in_place=True)
        rels = list(coramin.relaxations.relaxation_data_objects(m))
        self.assertEqual(len(rels), 1)
        r = rels[0]
        self.assertEqual(r.relaxation_side, coramin.utils.RelaxationSide.BOTH)

    def test_exp(self):
        self.helper(func=pe.exp, lb=-1, ub=1)

    def test_log(self):
        self.helper(func=pe.log, lb=0.5, ub=1.5)

    def test_log10(self):
        self.helper(func=pe.log10, lb=0.5, ub=1.5)

    def test_quadratic(self):
        def func(x):
            return x**2
        self.helper(func=func, lb=-1, ub=2)

    def test_arctan(self):
        self.helper(func=pe.atan, lb=-1, ub=1)

    def test_sin(self):
        self.helper(func=pe.sin, lb=-1, ub=1)

    def test_cos(self):
        self.helper(func=pe.cos, lb=-1, ub=1)


class TestDegree0(unittest.TestCase):
    def helper(self, func, param_val):
        m = pe.ConcreteModel()
        m.x = pe.Var(bounds=(-1, 1))
        m.aux = pe.Var()
        m.p = pe.Param(mutable=True, initialize=param_val)
        m.c = pe.Constraint(expr=m.aux == func(m.p) * m.x**2)
        self.assertIn(m.p, ComponentSet(identify_components(m.c.body, [_ParamData, SimpleParam])))
        coramin.relaxations.relax(m, in_place=True)
        rels = list(coramin.relaxations.relaxation_data_objects(m))
        self.assertEqual(len(rels), 1)
        r = rels[0]
        self.assertIsInstance(r, coramin.relaxations.PWXSquaredRelaxationData)
        self.assertIn(m.p, ComponentSet(identify_components(m.aux_cons[1].body, [_ParamData, SimpleParam])))

    def test_exp(self):
        self.helper(func=pe.exp, param_val=1)

    def test_log(self):
        self.helper(func=pe.log, param_val=1.5)

    def test_log10(self):
        self.helper(func=pe.log10, param_val=1.5)

    def test_arctan(self):
        self.helper(func=pe.atan, param_val=0.5)

    def test_sin(self):
        self.helper(func=pe.sin, param_val=0.5)

    def test_cos(self):
        self.helper(func=pe.cos, param_val=0.5)
