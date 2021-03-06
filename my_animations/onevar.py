from manimlib.imports import *
import typing
import itertools
import collections
import math


def set_colors(object: typing.Union[Mobject, Group, typing.Sequence], colors: typing.List[str]) -> object:
    [object[i].set_color(color) for i, color in enumerate(colors)]
    return object


def ReplacementMultiIndex(
    m1: Mobject, i1: typing.Iterable[typing.Union[int, typing.Sequence[int], range]],
    m2: Mobject, i2: typing.Iterable[typing.Union[int, typing.Sequence[int], range]],
    *, copy_first: bool = False, copy_second: bool = False, transformation: type = ReplacementTransform,
    fade_in: type = FadeIn, fade_out: type = FadeOut
):
    """
    Does a multi-index replacement.
    :param m1: The first object; is replaced.
    :param i1: The respective indexes.
    :param m2: The second object; is the replacer.
    :param i2: The respective replacer indexes.
    :param copy_first: If all replaced objects (in m1) should be copied. Defaults to False.
    :param copy_second: If all replacer objects (in m2) should be copied. Defaults to False.
    :param transformation: The transformation class to use (defaults to ReplacementTransform).
    :param fade_in: The transformation to use when ``None`` is specified on i1. Defaults to ``FadeIn``.
    :param fade_out: The transformation to use when ``None`` is specified on i2. Defaults to ``FadeOut``.
    :return:
    """
    i1 = list(i1)
    m_i2_enum = filter(lambda pair: isinstance(pair[1], collections.Iterable) and i1[0] is not None, enumerate(i2))
    multiple_i2 = list(map(lambda t: t[1], m_i2_enum))
    indexes_mult = map(lambda t: t[0], enumerate(multiple_i2))
    
    multiple_i1 = [i1[i] for i in indexes_mult]
    
    single_i1 = i1 if not multiple_i1 else filter(lambda el: el not in multiple_i1, i1)
    single_i2 = i2 if not multiple_i1 else filter(lambda el: el not in multiple_i2, i2)
    
    def copy_if_copy_first(obj):
        if copy_first and obj is not None:
            return obj.copy()
        return obj

    def copy_if_copy_second(obj):
        if copy_second and obj is not None:
            return obj.copy()
        return obj

    def converter(m, ii):
        if ii is None:
            return None

        if type(ii) == range or isinstance(ii, range):
            return m[ii.start:ii.stop:ii.step]

        if type(ii) in (list, tuple) or isinstance(ii, list) or isinstance(ii, tuple):
            return VGroup(*map(lambda i: m[i], ii))

        return m[ii]
    
    def resolve_transform(a1, a2):
        if a2 is None:
            return fade_out(a1)
        elif a1 is None:
            return fade_in(a2)
        else:
            return transformation(a1, a2)

    replacements = [
        resolve_transform(
            copy_if_copy_first(
                converter(m1, ii1)
            ),

            copy_if_copy_second(
                converter(m2, ii2)
            )
        ) for ii1, ii2 in zip(single_i1, single_i2)
    ] + sum([
        [
            resolve_transform(
                copy_if_copy_first(converter(m1, ii1)),
                copy_if_copy_second(converter(m2, ii2))
            ) for ii2 in itertools.islice(is2, 0, 1)  # just the first time this element appears; doesn't get copied
        ] + [
            resolve_transform(
                converter(m1, ii1).copy(),
                copy_if_copy_second(converter(m2, ii2))
            ) for ii2 in itertools.islice(is2, 1, None)  # others of this same element are necessarily copied
        ] for ii1, is2 in zip(multiple_i1, multiple_i2)
    ], [])
    return replacements


class Unwrite(Write):
    CONFIG = {
        "rate_func": lambda t: linear(1 - t),
        "remover": True
    }


class UnDrawBorderThenFill(DrawBorderThenFill):
    CONFIG = {
        "rate_func": lambda t: double_smooth(1 - t),
        "remover": True
    }


class ReplaceClockwiseTransform(ClockwiseTransform):
    CONFIG = {
        "replace_mobject_with_target_in_scene": True,
    }


class ReplaceCounterclockwiseTransform(CounterclockwiseTransform):
    CONFIG = {
        "replace_mobject_with_target_in_scene": True,
    }

class Simplifying(GraphScene):
    def construct(self):
        text1=TextMobject("Solve and Graph One Variable Inequalities")
        text2=TextMobject("Problem 20")
        text3=TextMobject("by Safin Singh")
        text2.next_to(text1,DOWN)
        text3.next_to(text1,DOWN)
        self.play(Write(text1))
        self.wait()
        self.play(Write(text2))
        self.wait()
        self.play(Transform(text2,text3))
        self.play(FadeOut(text2))
        self.play(FadeOut(text1))
        eq1=TexMobject("28-7x","\\leq","-4(-7x-7)")
        eq2=TexMobject("28-7x","\\leq","28x+28")
        eq2_v2=TexMobject("28","-7x","\\leq","28x","+28")
        eq2_v2_indices = [1, 2, 3]
        eq3=TexMobject("0","\\leq","35x")
        eq4=TexMobject("0","\\leq","x")
        eq5=TexMobject("x","\\geq","0")
        dot=Dot(radius=0.2,fill_color=RED,fill_opacity=1)
        self.play(Write(eq1))
        self.wait()
        self.play(*ReplacementMultiIndex(eq1,[0,1,2],eq2,[0,1,2],transformation=Transform))
        self.remove(eq1)
        self.add(eq2_v2)
        self.wait()
        self.play(FadeOut(eq2_v2[0]),FadeOut(eq2_v2[4]))
        self.play(VGroup(*[eq2_v2[i] for i in eq2_v2_indices]).move_to, ORIGIN)
        self.wait()
        self.play(ReplacementTransform(VGroup(*[eq2_v2[i] for i in eq2_v2_indices]), eq3))
        self.wait()
        self.play(ReplacementTransform(eq3,eq4))
        self.wait()
        self.play(ClockwiseTransform(eq4,eq5))
        self.play(eq4.move_to, UP)
        myNL = NumberLine(
            x_min=-5,
            x_max=5,
            numbers_to_show=range(-4,4),
            include_numbers=True
        )
        myNL.add_tip(at_start=True, reset_endpoints=False)
        myNL.add_tip(at_start=False, reset_endpoints=False)
        self.play(Write(myNL))
        dot.move_to(myNL.number_to_point(0))
        self.wait()
        self.play(ReplacementTransform(eq4[1].copy(),dot))
        line = Line(myNL.number_to_point(0),myNL.number_to_point(3),color=RED, stroke_width=5)
        line.add_tip(at_start=False, reset_endpoints=True)
        self.wait()
        self.play(ShowCreation(line))
        myVG = VGroup(eq4,myNL,line,dot)
        myRect = Rectangle(height=3, width=11)
        self.wait()
        self.play(ShowCreation(myRect),myVG.move_to,ORIGIN,run_time=1.5)
        self.wait()
        self.play(FadeOut(myVG),FadeOut(myRect))
        self.wait()