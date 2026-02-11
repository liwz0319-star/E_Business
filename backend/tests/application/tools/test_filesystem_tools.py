"""
File System Tools Unit Tests
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path

from app.application.tools.filesystem_tools import FileSystemTools


@pytest.fixture
def temp_workspace():
    """创建临时工作区目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def fs_tools(temp_workspace):
    """创建 FileSystemTools 实例"""
    return FileSystemTools(base_path=temp_workspace)


class TestFileSystemTools:
    """测试 FileSystemTools 功能"""

    def test_create_workspace(self, fs_tools):
        """测试创建工作区"""
        workflow_id = "test-workflow-123"
        workspace_path = fs_tools.create_workspace(workflow_id)

        # 验证目录结构
        assert os.path.exists(workspace_path)
        assert os.path.exists(os.path.join(workspace_path, "input"))
        assert os.path.exists(os.path.join(workspace_path, "workspace"))
        assert os.path.exists(os.path.join(workspace_path, "artifacts", "copy"))
        assert os.path.exists(os.path.join(workspace_path, "artifacts", "images"))
        assert os.path.exists(os.path.join(workspace_path, "artifacts", "video"))
        assert os.path.exists(os.path.join(workspace_path, "logs"))

    def test_write_and_read_file(self, fs_tools, temp_workspace):
        """测试文件读写"""
        workflow_id = "test-workflow-456"
        workspace = fs_tools.create_workspace(workflow_id)

        file_path = f"{workflow_id}/workspace/test.txt"
        content = "Hello, World!"

        fs_tools.write_file(file_path, content)
        read_content = fs_tools.read_file(file_path)

        assert read_content == content

    def test_write_and_read_json(self, fs_tools, temp_workspace):
        """测试 JSON 读写"""
        workflow_id = "test-workflow-789"
        workspace = fs_tools.create_workspace(workflow_id)

        file_path = f"{workflow_id}/workspace/data.json"
        data = {"key": "value", "number": 42}

        fs_tools.write_json(file_path, data)
        read_data = fs_tools.read_json(file_path)

        assert read_data == data

    def test_path_validation_security(self, fs_tools):
        """测试路径安全验证 - 防止路径遍历攻击"""
        with pytest.raises(ValueError, match="Path security violation"):
            fs_tools._validate_path("../../../etc/passwd")

        with pytest.raises(ValueError, match="Path security violation"):
            fs_tools._validate_path("../../secrets.txt")

    def test_list_dir(self, fs_tools, temp_workspace):
        """测试目录列表"""
        workflow_id = "test-workflow-list"
        workspace = fs_tools.create_workspace(workflow_id)

        # 创建测试文件
        fs_tools.write_file(f"{workflow_id}/workspace/file1.txt", "content1")
        fs_tools.write_file(f"{workflow_id}/workspace/file2.txt", "content2")

        files = fs_tools.list_dir(f"{workflow_id}/workspace")

        assert len(files) == 2
        assert any("file1.txt" in f for f in files)
        assert any("file2.txt" in f for f in files)

    def test_exists(self, fs_tools, temp_workspace):
        """测试文件存在性检查"""
        workflow_id = "test-workflow-exists"
        workspace = fs_tools.create_workspace(workflow_id)

        file_path = f"{workflow_id}/workspace/test.txt"
        assert not fs_tools.exists(file_path)

        fs_tools.write_file(file_path, "content")
        assert fs_tools.exists(file_path)
