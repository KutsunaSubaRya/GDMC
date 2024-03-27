from gdpc.vector_tools import Box


def local_lobby_dynamic_offset(original_area: Box):
    start_x, start_y, start_z = original_area.begin
    end_x, end_y, end_z = original_area.end
    offset_x = ((end_x - start_x) - 120) // 2
    offset_z = ((end_z - start_z) - 120) // 2
    return offset_x, offset_z
