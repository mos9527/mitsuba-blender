if "bpy" in locals():
    import importlib
    if "mi_props_utils" in locals():
        importlib.reload(mi_props_utils)

import bpy

from .mi_props_utils import get_references_by_type

#################
##  Utilities  ##
#################

_fileformat_values = {
    'openexr': 'OPEN_EXR',
    'exr': 'OPEN_EXR',
    # FIXME: Support other file formats
}

def mi_fileformat_to_bl_fileformat(mi_context, mi_file_format):
    if mi_file_format not in _fileformat_values:
        mi_context.log(f'Mitsuba Film image file format "{mi_file_format}" has no direct Blender equivalent; leaving it unchanged.', 'WARN')
        return None
    return _fileformat_values[mi_file_format]

_pixelformat_values = {
    'rgb': 'RGB',
    'rgba': 'RGBA',
    # FIXME: Support other pixel formats
}

def mi_pixelformat_to_bl_pixelformat(mi_context, mi_pixel_format):
    if mi_pixel_format not in _pixelformat_values:
        mi_context.log(f'Mitsuba Film image pixel format "{mi_pixel_format}" has no direct Blender equivalent; leaving it unchanged.', 'WARN')
        return None
    return _pixelformat_values[mi_pixel_format]

_componentformat_values = {
    'float16': '16',
    'float32': '32',
    # FIXME: Support other component formats
}

def mi_componentformat_to_bl_componentformat(mi_context, mi_component_format):
    if mi_component_format not in _componentformat_values:
        mi_context.log(f'Mitsuba Film image component format "{mi_component_format}" has no direct Blender equivalent; leaving it unchanged.', 'WARN')
        return None
    return _componentformat_values[mi_component_format]

#############################
##  Integrator properties  ##
#############################

def apply_mi_path_properties(mi_context, mi_props, bl_props=None):
    # Cycles properties
    bl_renderer = mi_context.bl_scene.cycles
    if hasattr(bl_renderer, 'progressive'):
        bl_renderer.progressive = 'PATH'
    bl_max_bounces = mi_props.get('max_depth', 1024)
    bl_renderer.max_bounces = bl_max_bounces
    bl_renderer.diffuse_bounces = bl_max_bounces
    bl_renderer.glossy_bounces = bl_max_bounces
    bl_renderer.transparent_max_bounces = bl_max_bounces
    bl_renderer.transmission_bounces = bl_max_bounces
    bl_renderer.volume_bounces = bl_max_bounces
    bl_renderer.min_light_bounces = mi_props.get('rr_depth', 5)

    return True

def apply_mi_volpath_properties(mi_context, mi_props, bl_props=None):
    # volpath maps to Cycles path integrator (Cycles handles volumes natively)
    mi_context.log('Mitsuba Integrator "volpath" maps to path integrator in Cycles.', 'WARN')

    bl_renderer = mi_context.bl_scene.cycles
    if hasattr(bl_renderer, 'progressive'):
        bl_renderer.progressive = 'PATH'
    bl_max_bounces = mi_props.get('max_depth', 1024)
    bl_renderer.max_bounces = bl_max_bounces
    bl_renderer.diffuse_bounces = bl_max_bounces
    bl_renderer.glossy_bounces = bl_max_bounces
    bl_renderer.transparent_max_bounces = bl_max_bounces
    bl_renderer.transmission_bounces = bl_max_bounces
    bl_renderer.volume_bounces = bl_max_bounces
    bl_renderer.min_light_bounces = mi_props.get('rr_depth', 5)

    return True

def apply_mi_moment_properties(mi_context, mi_props, bl_props=None):
    # Moment integrator maps to path in Cycles
    mi_context.log('Mitsuba Integrator "moment" maps to path integrator in Cycles.', 'WARN')

    # Cycles properties — fall back to path defaults
    bl_renderer = mi_context.bl_scene.cycles
    if hasattr(bl_renderer, 'progressive'):
        bl_renderer.progressive = 'PATH'

    return True

_mi_integrator_properties_converters = {
    'path': apply_mi_path_properties,
    'volpath': apply_mi_volpath_properties,
    'moment': apply_mi_moment_properties,
}

def apply_mi_integrator_properties(mi_context, mi_props, bl_integrator_props=None):
    # The modified plugin does not need to configure the Cycles integrator from Mitsuba's
    # integrator node. Known integrators (path / volpath / moment) still get translated
    # to set sane bounce defaults, but any unknown integrator (e.g. "sppm", "bdpt",
    # "ptracer", ...) is silently skipped instead of raising an ERROR.
    mi_integrator_type = mi_props.plugin_name()
    if mi_integrator_type not in _mi_integrator_properties_converters:
        mi_context.log(
            f'Mitsuba Integrator "{mi_integrator_type}" has no Cycles equivalent; skipping integrator configuration.',
            'INFO',
        )
        return True

    return _mi_integrator_properties_converters[mi_integrator_type](mi_context, mi_props, bl_integrator_props)

##########################
##  RFilter properties  ##
##########################

def apply_mi_tent_properties(mi_context, mi_props):
    # Cycles properties
    # NOTE: Cycles does not have any equivalent to the tent filter

    return True

def apply_mi_box_properties(mi_context, mi_props):
    bl_renderer = mi_context.bl_scene.cycles
    # Cycles properties
    bl_renderer.pixel_filter_type = 'BOX'

    return True

def apply_mi_gaussian_properties(mi_context, mi_props):
    bl_renderer = mi_context.bl_scene.cycles
    # Cycles properties
    bl_renderer.pixel_filter_type = 'GAUSSIAN'
    bl_renderer.filter_width = mi_props.get('stddev', 0.5)
    return True

_mi_rfilter_properties_converters = {
    'box': apply_mi_box_properties,
    'tent': apply_mi_tent_properties,
    'gaussian': apply_mi_gaussian_properties,
}

def apply_mi_rfilter_properties(mi_context, mi_props):
    mi_rfilter_type = mi_props.plugin_name()
    if mi_rfilter_type not in _mi_rfilter_properties_converters:
        mi_context.log(f'Mitsuba Reconstruction Filter "{mi_rfilter_type}" is not supported.', 'ERROR')
        return False

    return _mi_rfilter_properties_converters[mi_rfilter_type](mi_context, mi_props)

##########################
##  Sampler properties  ##
##########################

def apply_mi_independent_properties(mi_context, mi_props):
    bl_renderer = mi_context.bl_scene.cycles
    # Cycles properties
    if bpy.app.version < (3, 5, 0):
        bl_renderer.sampling_pattern = 'SOBOL'
    elif bpy.app.version < (4, 0, 0):
        bl_renderer.sampling_pattern = 'SOBOL_BURLEY'
    else:
        bl_renderer.sampling_pattern = 'AUTOMATIC'
    bl_renderer.samples = mi_props.get('sample_count', 4)
    bl_renderer.preview_samples = mi_props.get('sample_count', 4)
    bl_renderer.seed = mi_props.get('seed', 0)
    return True

def apply_mi_stratified_properties(mi_context, mi_props):
    bl_renderer = mi_context.bl_scene.cycles
    # Cycles properties
    if bpy.app.version < (3, 5, 0):
        bl_renderer.sampling_pattern = 'SOBOL'
    elif bpy.app.version < (4, 0, 0):
        bl_renderer.sampling_pattern = 'SOBOL_BURLEY'
    else:
        bl_renderer.sampling_pattern = 'AUTOMATIC'
    bl_renderer.samples = mi_props.get('sample_count', 4)
    bl_renderer.seed = mi_props.get('seed', 0)
    return True

def apply_mi_multijitter_properties(mi_context, mi_props):
    bl_renderer = mi_context.bl_scene.cycles
    # Cycles properties
    if bpy.app.version < (3, 0, 0):
        bl_renderer.sampling_pattern = 'CORRELATED_MUTI_JITTER'
    elif bpy.app.version < (3, 5, 0):
        bl_renderer.sampling_pattern = 'PROGRESSIVE_MULTI_JITTER'
    else:
        bl_renderer.sampling_pattern = 'TABULATED_SOBOL'
    bl_renderer.samples = mi_props.get('sample_count', 4)
    bl_renderer.seed = mi_props.get('seed', 0)
    return True

_mi_sampler_properties_converters = {
    'independent': apply_mi_independent_properties,
    'stratified': apply_mi_stratified_properties,
    'multijitter': apply_mi_multijitter_properties,
}

def apply_mi_sampler_properties(mi_context, mi_props):
    mi_sampler_type = mi_props.plugin_name()
    if mi_sampler_type not in _mi_sampler_properties_converters:
        mi_context.log(f'Mitsuba Sampler "{mi_sampler_type}" is not supported.', 'ERROR')
        return False

    return _mi_sampler_properties_converters[mi_sampler_type](mi_context, mi_props)

#######################
##  Film properties  ##
#######################

def apply_mi_hdrfilm_properties(mi_context, mi_props):
    mi_context.bl_scene.render.resolution_percentage = 100
    render_dims = (mi_props.get('width', 768), mi_props.get('height', 576))
    mi_context.bl_scene.render.resolution_x = render_dims[0]
    mi_context.bl_scene.render.resolution_y = render_dims[1]

    # Only apply format properties when they map cleanly to Blender. Unsupported values
    # are logged as WARN inside the helpers and return None, which we skip here instead of
    # assigning None to Blender properties (which would raise).
    bl_fileformat = mi_fileformat_to_bl_fileformat(mi_context, mi_props.get('file_format', 'openexr'))
    if bl_fileformat is not None:
        mi_context.bl_scene.render.image_settings.file_format = bl_fileformat
    bl_pixelformat = mi_pixelformat_to_bl_pixelformat(mi_context, mi_props.get('pixel_format', 'rgba'))
    if bl_pixelformat is not None:
        mi_context.bl_scene.render.image_settings.color_mode = bl_pixelformat
    bl_componentformat = mi_componentformat_to_bl_componentformat(mi_context, mi_props.get('component_format', 'float16'))
    if bl_componentformat is not None:
        mi_context.bl_scene.render.image_settings.color_depth = bl_componentformat

    crop_keys = ['crop_offset_x', 'crop_offset_y', 'crop_width', 'crop_height']
    if any(key in mi_props for key in crop_keys):
        mi_context.bl_scene.render.use_border = True
        # FIXME: Do we want to crop the resulting image ?
        mi_context.bl_scene.render.use_crop_to_border = True
        offset_x = mi_props.get('crop_offset_x', 0)
        offset_y = mi_props.get('crop_offset_y', 0)
        width = mi_props.get('crop_width', render_dims[0])
        height = mi_props.get('crop_height', render_dims[1])
        mi_context.bl_scene.render.border_min_x = offset_x / render_dims[0]
        mi_context.bl_scene.render.border_max_x = (offset_x + width) / render_dims[0]
        mi_context.bl_scene.render.border_min_y = offset_y / render_dims[1]
        mi_context.bl_scene.render.border_max_y = (offset_y + height) / render_dims[1]
    return True

def apply_mi_ldrfilm_properties(mi_context, mi_props):
    # ldrfilm has the same resolution / crop semantics as hdrfilm; reuse the handler. Any
    # low-dynamic-range file/pixel/component formats (png / jpeg / rgb / uint8 ...) will
    # fall through the WARN-and-skip path added to the *_to_bl_* helpers above.
    return apply_mi_hdrfilm_properties(mi_context, mi_props)

_mi_film_properties_converters = {
    'hdrfilm': apply_mi_hdrfilm_properties,
    'ldrfilm': apply_mi_ldrfilm_properties,
}

def apply_mi_film_properties(mi_context, mi_props):
    mi_film_type = mi_props.plugin_name()
    if mi_film_type not in _mi_film_properties_converters:
        # Don't error out on exotic films (tonemapfilm, specfilm, ...). The modified
        # plugin does not strictly need the film settings propagated, so skip quietly.
        mi_context.log(
            f'Mitsuba Film "{mi_film_type}" has no direct Blender equivalent; skipping film configuration.',
            'INFO',
        )
        return True

    return _mi_film_properties_converters[mi_film_type](mi_context, mi_props)

###########################
##  Renderer properties  ##
###########################

def init_cycles_renderer(mi_context):
    mi_context.bl_scene.render.engine = 'CYCLES'
    mi_context.bl_scene.cycles.device = 'GPU'
    return True
