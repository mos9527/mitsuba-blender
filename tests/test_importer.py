import bpy

import pytest

from fixtures import *

@pytest.mark.parametrize("xml_scene", ["scenes/empty.xml"])
def test_importer_override_current_scene_conserves_name(resource_resolver, xml_scene):
    scene_file = resource_resolver.get_absolute_resource_path(xml_scene)

    assert len(bpy.data.scenes) == 1
    scene_name_before = bpy.data.scenes[0].name

    assert bpy.ops.import_scene.mitsuba(filepath=scene_file, override_scene=True) == {'FINISHED'}

    assert len(bpy.data.scenes) == 1
    assert bpy.data.scenes[0].name == scene_name_before

@pytest.mark.parametrize("xml_scene", ["scenes/empty.xml"])
def test_importer_multiple_scene_imports(resource_resolver, xml_scene):
    scene_file = resource_resolver.get_absolute_resource_path(xml_scene)

    assert len(bpy.data.scenes) == 1

    assert bpy.ops.import_scene.mitsuba(filepath=scene_file, override_scene=False) == {'FINISHED'}
    object_count_before = len(bpy.context.scene.objects)

    assert len(bpy.data.scenes) == 2

    assert bpy.ops.import_scene.mitsuba(filepath=scene_file, override_scene=False) == {'FINISHED'}
    assert len(bpy.context.scene.objects) == object_count_before

    assert len(bpy.data.scenes) == 2

@pytest.mark.parametrize("xml_scene", ["scenes/empty.xml"])
def test_importer_set_new_scene_as_active(resource_resolver, xml_scene):
    scene_file = resource_resolver.get_absolute_resource_path(xml_scene)

    assert len(bpy.data.scenes) == 1
    scene_name_before = bpy.data.scenes[0].name

    assert bpy.ops.import_scene.mitsuba(filepath=scene_file, override_scene=False) == {'FINISHED'}

    assert len(bpy.data.scenes) == 2
    assert bpy.context.scene.name != scene_name_before

@pytest.mark.parametrize("xml_scene", ["scenes/empty.xml"])
def test_importer_initializes_cycles_renderer(resource_resolver, xml_scene):
    scene_file = resource_resolver.get_absolute_resource_path(xml_scene)

    assert bpy.ops.import_scene.mitsuba(filepath=scene_file) == {'FINISHED'}

    assert bpy.context.scene.render.engine == 'CYCLES'
    assert bpy.context.scene.cycles.device == 'GPU'

@pytest.mark.parametrize("xml_scene", ["scenes/integrator_path.xml"])
def test_importer_path_integrator(resource_resolver, mitsuba_scene_parser, xml_scene):
    scene_file = resource_resolver.get_absolute_resource_path(xml_scene)
    mitsuba_scene_parser.load_xml(scene_file)

    mi_integrator = mitsuba_scene_parser.get_props_by_name('path')
    assert mi_integrator

    assert bpy.ops.import_scene.mitsuba(filepath=scene_file) == {'FINISHED'}

    bl_scene = bpy.context.scene
    bl_cycles = bl_scene.cycles
    assert bl_cycles.max_bounces == mi_integrator.get('max_depth')
    assert bl_cycles.min_light_bounces == mi_integrator.get('rr_depth')

    # assert len(mi_integrator.unqueried()) == 0

@pytest.mark.parametrize("xml_scene", ["scenes/integrator_moment.xml"])
def test_importer_moment_integrator(resource_resolver, mitsuba_scene_parser, xml_scene):
    scene_file = resource_resolver.get_absolute_resource_path(xml_scene)
    mitsuba_scene_parser.load_xml(scene_file)

    mi_integrator = mitsuba_scene_parser.get_props_by_name('moment')
    assert mi_integrator

    assert bpy.ops.import_scene.mitsuba(filepath=scene_file) == {'FINISHED'}

    # moment integrator maps to path in Cycles — just verify engine is set
    bl_scene = bpy.context.scene
    assert bl_scene.render.engine == 'CYCLES'

    # assert len(mi_integrator.unqueried()) == 0

@pytest.mark.parametrize("xml_scene", ["scenes/sampler_independent.xml"])
def test_importer_independent_sampler(resource_resolver, mitsuba_scene_parser, xml_scene):
    scene_file = resource_resolver.get_absolute_resource_path(xml_scene)
    mitsuba_scene_parser.load_xml(scene_file)

    mi_sampler = mitsuba_scene_parser.get_props_by_name('independent')
    assert mi_sampler

    assert bpy.ops.import_scene.mitsuba(filepath=scene_file) == {'FINISHED'}

    bl_cycles = bpy.context.scene.cycles
    assert bl_cycles.samples == mi_sampler.get('sample_count')
    assert bl_cycles.seed == mi_sampler.get('seed')

    # assert len(mi_sampler.unqueried()) == 0

@pytest.mark.parametrize("xml_scene", ["scenes/sampler_stratified.xml"])
def test_importer_stratified_sampler(resource_resolver, mitsuba_scene_parser, xml_scene):
    scene_file = resource_resolver.get_absolute_resource_path(xml_scene)
    mitsuba_scene_parser.load_xml(scene_file)

    mi_sampler = mitsuba_scene_parser.get_props_by_name('stratified')
    assert mi_sampler

    assert bpy.ops.import_scene.mitsuba(filepath=scene_file) == {'FINISHED'}

    bl_cycles = bpy.context.scene.cycles
    assert bl_cycles.samples == mi_sampler.get('sample_count')
    assert bl_cycles.seed == mi_sampler.get('seed')

    # assert len(mi_sampler.unqueried()) == 0

@pytest.mark.parametrize("xml_scene", ["scenes/sampler_multijitter.xml"])
def test_importer_multijitter_sampler(resource_resolver, mitsuba_scene_parser, xml_scene):
    scene_file = resource_resolver.get_absolute_resource_path(xml_scene)
    mitsuba_scene_parser.load_xml(scene_file)

    mi_sampler = mitsuba_scene_parser.get_props_by_name('multijitter')
    assert mi_sampler

    assert bpy.ops.import_scene.mitsuba(filepath=scene_file) == {'FINISHED'}

    bl_cycles = bpy.context.scene.cycles
    assert bl_cycles.samples == mi_sampler.get('sample_count')
    assert bl_cycles.seed == mi_sampler.get('seed')

    # assert len(mi_sampler.unqueried()) == 0

@pytest.mark.parametrize("xml_scene", ["scenes/rfilter_box.xml"])
def test_importer_box_rfilter(resource_resolver, mitsuba_scene_parser, xml_scene):
    scene_file = resource_resolver.get_absolute_resource_path(xml_scene)
    mitsuba_scene_parser.load_xml(scene_file)

    mi_rfilter = mitsuba_scene_parser.get_props_by_name('box')
    assert mi_rfilter

    assert bpy.ops.import_scene.mitsuba(filepath=scene_file) == {'FINISHED'}

    bl_cycles = bpy.context.scene.cycles
    assert bl_cycles.pixel_filter_type == 'BOX'

    # assert len(mi_rfilter.unqueried()) == 0

@pytest.mark.parametrize("xml_scene", ["scenes/rfilter_tent.xml"])
def test_importer_tent_rfilter(resource_resolver, mitsuba_scene_parser, xml_scene):
    scene_file = resource_resolver.get_absolute_resource_path(xml_scene)
    mitsuba_scene_parser.load_xml(scene_file)

    mi_rfilter = mitsuba_scene_parser.get_props_by_name('tent')
    assert mi_rfilter

    assert bpy.ops.import_scene.mitsuba(filepath=scene_file) == {'FINISHED'}

    # Cycles has no tent filter equivalent — just verify import succeeds
    assert bpy.context.scene.render.engine == 'CYCLES'

    # assert len(mi_rfilter.unqueried()) == 0

@pytest.mark.parametrize("xml_scene", ["scenes/rfilter_gaussian.xml"])
def test_importer_gaussian_rfilter(resource_resolver, mitsuba_scene_parser, xml_scene):
    scene_file = resource_resolver.get_absolute_resource_path(xml_scene)
    mitsuba_scene_parser.load_xml(scene_file)

    mi_rfilter = mitsuba_scene_parser.get_props_by_name('gaussian')
    assert mi_rfilter

    assert bpy.ops.import_scene.mitsuba(filepath=scene_file) == {'FINISHED'}

    bl_cycles = bpy.context.scene.cycles
    assert bl_cycles.pixel_filter_type == 'GAUSSIAN'

    # assert len(mi_rfilter.unqueried()) == 0

@pytest.mark.parametrize("xml_scene", ["scenes/film_hdrfilm.xml", "scenes/film_hdrfilm_crop.xml"])
def test_importer_hdrfilm_film(resource_resolver, mitsuba_scene_parser, xml_scene):
    scene_file = resource_resolver.get_absolute_resource_path(xml_scene)
    mitsuba_scene_parser.load_xml(scene_file)

    mi_film = mitsuba_scene_parser.get_props_by_name('hdrfilm')
    assert mi_film

    assert bpy.ops.import_scene.mitsuba(filepath=scene_file) == {'FINISHED'}

    bl_render = bpy.context.scene.render
    assert bl_render.resolution_percentage == 100
    assert bl_render.resolution_x == mi_film.get('width')
    assert bl_render.resolution_y == mi_film.get('height')
    assert bl_render.image_settings.file_format == 'OPEN_EXR'
    assert bl_render.image_settings.color_mode == 'RGBA'
    assert bl_render.image_settings.color_depth == '32'
    if 'crop' in xml_scene:
        assert bl_render.use_border == True
        assert bl_render.border_min_x == 0.0
        assert bl_render.border_min_y == 0.0
        assert bl_render.border_max_x == 0.5
        assert bl_render.border_max_y == 0.5
    else:
        assert bl_render.use_border == False

    # assert len(mi_film.unqueried()) == 0
