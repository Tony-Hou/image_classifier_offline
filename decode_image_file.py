#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/27 下午3:56
# @Author  : houlinjie
# @Site    : 
# @File    : decode_image_file.py
# @Software: PyCharm

@tf_export('image.is_jpeg')
def is_jpeg(contents, name=None):
  r"""Convenience function to check if the 'contents' encodes a JPEG image.
  Args:
    contents: 0-D `string`. The encoded image bytes.
    name: A name for the operation (optional)
  Returns:
     A scalar boolean tensor indicating if 'contents' may be a JPEG image.
     is_jpeg is susceptible to false positives.
  """
  # Normal JPEGs start with \xff\xd8\xff\xe0
  # JPEG with EXIF stats with \xff\xd8\xff\xe1
  # Use \xff\xd8\xff to cover both.
  with ops.name_scope(name, 'is_jpeg'):
    substr = string_ops.substr(contents, 0, 3)
    return math_ops.equal(substr, b'\xff\xd8\xff', name=name)


def _is_png(contents, name=None):
  r"""Convenience function to check if the 'contents' encodes a PNG image.
  Args:
    contents: 0-D `string`. The encoded image bytes.
    name: A name for the operation (optional)
  Returns:
     A scalar boolean tensor indicating if 'contents' may be a PNG image.
     is_png is susceptible to false positives.
  """
  with ops.name_scope(name, 'is_png'):
    substr = string_ops.substr(contents, 0, 3)
    return math_ops.equal(substr, b'\211PN', name=name)


@tf_export('image.decode_image')
def decode_image(contents, channels=None, dtype=dtypes.uint8, name=None):
  """Convenience function for `decode_bmp`, `decode_gif`, `decode_jpeg`,
  and `decode_png`.
  Detects whether an image is a BMP, GIF, JPEG, or PNG, and performs the
  appropriate operation to convert the input bytes `string` into a `Tensor`
  of type `dtype`.
  Note: `decode_gif` returns a 4-D array `[num_frames, height, width, 3]`, as
  opposed to `decode_bmp`, `decode_jpeg` and `decode_png`, which return 3-D
  arrays `[height, width, num_channels]`. Make sure to take this into account
  when constructing your graph if you are intermixing GIF files with BMP, JPEG,
  and/or PNG files.
  Args:
    contents: 0-D `string`. The encoded image bytes.
    channels: An optional `int`. Defaults to `0`. Number of color channels for
      the decoded image.
    dtype: The desired DType of the returned `Tensor`.
    name: A name for the operation (optional)
  Returns:
    `Tensor` with type `dtype` and shape `[height, width, num_channels]` for
      BMP, JPEG, and PNG images and shape `[num_frames, height, width, 3]` for
      GIF images.
  Raises:
    ValueError: On incorrect number of channels.
  """
  with ops.name_scope(name, 'decode_image'):
      if channels not in (None, 0, 1, 3, 4):
          raise ValueError('channels must be in (None, 0, 1, 3, 4)')
      substr = string_ops.substr(contents, 0, 3)

      def _bmp():
          """Decodes a GIF image."""
          signature = string_ops.substr(contents, 0, 2)
          # Create assert op to check that bytes are BMP decodable
          is_bmp = math_ops.equal(signature, 'BM', name='is_bmp')
          decode_msg = 'Unable to decode bytes as JPEG, PNG, GIF, or BMP'
          assert_decode = control_flow_ops.Assert(is_bmp, [decode_msg])
          bmp_channels = 0 if channels is None else channels
          good_channels = math_ops.not_equal(bmp_channels, 1, name='check_channels')
          channels_msg = 'Channels must be in (None, 0, 3) when decoding BMP images'
          assert_channels = control_flow_ops.Assert(good_channels, [channels_msg])
          with ops.control_dependencies([assert_decode, assert_channels]):
              return convert_image_dtype(gen_image_ops.decode_bmp(contents), dtype)

      def _gif():
          # Create assert to make sure that channels is not set to 1
          # Already checked above that channels is in (None, 0, 1, 3)

          gif_channels = 0 if channels is None else channels
          good_channels = math_ops.logical_and(
              math_ops.not_equal(gif_channels, 1, name='check_gif_channels'),
              math_ops.not_equal(gif_channels, 4, name='check_gif_channels'))
          channels_msg = 'Channels must be in (None, 0, 3) when decoding GIF images'
          assert_channels = control_flow_ops.Assert(good_channels, [channels_msg])
          with ops.control_dependencies([assert_channels]):
              return convert_image_dtype(gen_image_ops.decode_gif(contents), dtype)

      def check_gif():
          # Create assert op to check that bytes are GIF decodable
          is_gif = math_ops.equal(substr, b'\x47\x49\x46', name='is_gif')
          return control_flow_ops.cond(is_gif, _gif, _bmp, name='cond_gif')

      def _png():
          """Decodes a PNG image."""
          return convert_image_dtype(
              gen_image_ops.decode_png(contents, channels,
                                       dtype=dtypes.uint8
                                       if dtype == dtypes.uint8
                                       else dtypes.uint16), dtype)

      def check_png():
          """Checks if an image is PNG."""
          return control_flow_ops.cond(
              _is_png(contents), _png, check_gif, name='cond_png')

      def _jpeg():
          """Decodes a jpeg image."""
          jpeg_channels = 0 if channels is None else channels
          good_channels = math_ops.not_equal(
              jpeg_channels, 4, name='check_jpeg_channels')
          channels_msg = ('Channels must be in (None, 0, 1, 3) when decoding JPEG '
                          'images')
          assert_channels = control_flow_ops.Assert(good_channels, [channels_msg])
          with ops.control_dependencies([assert_channels]):
              return convert_image_dtype(
                  gen_image_ops.decode_jpeg(contents, channels), dtype)

      # Decode normal JPEG images (start with \xff\xd8\xff\xe0)
      # as well as JPEG images with EXIF data (start with \xff\xd8\xff\xe1).
      return control_flow_ops.cond(
          is_jpeg(contents), _jpeg, check_png, name='cond_jpeg')