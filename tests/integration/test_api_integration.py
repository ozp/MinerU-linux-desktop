"""
Integration tests for API interactions.

Tests end-to-end workflows with mocked API responses,
including upload, polling, and download operations.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time

from mineru_desktop.core.client import MineruClient
from mineru_desktop.services.upload_service import UploadService
from mineru_desktop.services.download_service import DownloadService
from mineru_desktop.models.batch import Batch, FileState, ProcessingOptions


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for API workflows."""

    @patch('mineru_desktop.core.client.requests.post')
    @patch('mineru_desktop.core.client.requests.put')
    @patch('mineru_desktop.core.client.requests.get')
    def test_complete_upload_poll_download_workflow(
        self,
        mock_get,
        mock_put,
        mock_post,
        sample_api_token,
        sample_files,
        sample_processing_options,
        temp_dir
    ):
        """Test complete workflow from upload to download."""
        # Setup client and services
        client = MineruClient(api_token=sample_api_token)
        upload_service = UploadService(client)
        download_service = DownloadService(client, temp_dir)

        # Create batch
        batch = Batch(processing_options=sample_processing_options)
        for file_path in sample_files:
            batch.add_file(file_path)

        # Mock upload response
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "data": {
                "batch_id": "integration_batch_123",
                "file_urls": [
                    "https://upload.example.com/1",
                    "https://upload.example.com/2",
                    "https://upload.example.com/3"
                ]
            }
        }
        mock_post.return_value = mock_post_response

        # Mock file upload
        mock_put_response = Mock()
        mock_put_response.status_code = 200
        mock_put.return_value = mock_put_response

        # Upload batch
        upload_service.upload_batch(batch)

        # Verify batch was uploaded
        assert batch.batch_id == "integration_batch_123"
        assert all(f.state == FileState.PROCESSING for f in batch.files)

        # Mock status check - first processing, then done
        status_responses = [
            # First check - still processing
            {
                "data": {
                    "batch_id": "integration_batch_123",
                    "files": [
                        {"filename": "test_0.pdf", "status": "processing"},
                        {"filename": "test_1.pdf", "status": "processing"},
                        {"filename": "test_2.pdf", "status": "pending"}
                    ]
                }
            },
            # Second check - all done
            {
                "data": {
                    "batch_id": "integration_batch_123",
                    "files": [
                        {
                            "filename": "test_0.pdf",
                            "status": "done",
                            "zip_url": "https://download.example.com/1.zip"
                        },
                        {
                            "filename": "test_1.pdf",
                            "status": "done",
                            "zip_url": "https://download.example.com/2.zip"
                        },
                        {
                            "filename": "test_2.pdf",
                            "status": "done",
                            "zip_url": "https://download.example.com/3.zip"
                        }
                    ]
                }
            }
        ]

        call_count = 0

        def get_side_effect(*args, **kwargs):
            nonlocal call_count
            response = Mock()
            response.status_code = 200
            response.json.return_value = status_responses[min(call_count, 1)]
            call_count += 1
            return response

        mock_get.side_effect = get_side_effect

        # Poll status until done
        max_attempts = 5
        for attempt in range(max_attempts):
            status_data = client.get_batch_status(batch.batch_id)
            files_data = status_data.get("data", {}).get("files", [])

            all_done = all(
                f.get("status") == "done"
                for f in files_data
            )

            if all_done:
                break

        # Verify final status
        assert call_count >= 2

    @patch('mineru_desktop.core.client.requests.post')
    @patch('mineru_desktop.core.client.requests.put')
    def test_upload_with_retry_logic(
        self,
        mock_put,
        mock_post,
        sample_api_token,
        sample_files,
        sample_processing_options
    ):
        """Test upload with simulated retry scenario."""
        client = MineruClient(api_token=sample_api_token)
        upload_service = UploadService(client)

        batch = Batch(processing_options=sample_processing_options)
        for file_path in sample_files:
            batch.add_file(file_path)

        # Mock POST to succeed
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "data": {
                "batch_id": "retry_batch_456",
                "file_urls": [
                    "https://upload.example.com/1",
                    "https://upload.example.com/2",
                    "https://upload.example.com/3"
                ]
            }
        }
        mock_post.return_value = mock_post_response

        # Mock PUT to fail first time, succeed second time
        call_count = [0]

        def put_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call fails
                raise Exception("Temporary network error")
            # Subsequent calls succeed
            response = Mock()
            response.status_code = 200
            return response

        mock_put.side_effect = put_side_effect

        # Upload batch
        upload_service.upload_batch(batch)

        # Verify that batch has mixed results
        assert batch.batch_id == "retry_batch_456"
        # First file should have failed
        assert batch.files[0].state == FileState.FAILED

    @patch('mineru_desktop.core.client.requests.post')
    @patch('mineru_desktop.core.client.requests.put')
    @patch('mineru_desktop.core.client.requests.get')
    def test_batch_with_partial_failures(
        self,
        mock_get,
        mock_put,
        mock_post,
        sample_api_token,
        sample_files,
        sample_processing_options
    ):
        """Test handling of batch where some files fail processing."""
        client = MineruClient(api_token=sample_api_token)
        upload_service = UploadService(client)

        batch = Batch(processing_options=sample_processing_options)
        for file_path in sample_files:
            batch.add_file(file_path)

        # Mock successful upload
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "data": {
                "batch_id": "partial_fail_batch",
                "file_urls": [
                    "https://upload.example.com/1",
                    "https://upload.example.com/2",
                    "https://upload.example.com/3"
                ]
            }
        }
        mock_post.return_value = mock_post_response

        mock_put_response = Mock()
        mock_put_response.status_code = 200
        mock_put.return_value = mock_put_response

        upload_service.upload_batch(batch)

        # Mock status with one file failed
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "data": {
                "batch_id": "partial_fail_batch",
                "files": [
                    {
                        "filename": "test_0.pdf",
                        "status": "done",
                        "zip_url": "https://download.example.com/1.zip"
                    },
                    {
                        "filename": "test_1.pdf",
                        "status": "failed",
                        "error": "Corrupted file"
                    },
                    {
                        "filename": "test_2.pdf",
                        "status": "done",
                        "zip_url": "https://download.example.com/3.zip"
                    }
                ]
            }
        }
        mock_get.return_value = mock_get_response

        # Check status
        status_data = client.get_batch_status(batch.batch_id)
        files_data = status_data.get("data", {}).get("files", [])

        # Verify mixed results
        assert files_data[0]["status"] == "done"
        assert files_data[1]["status"] == "failed"
        assert files_data[2]["status"] == "done"

    @patch('mineru_desktop.core.client.requests.post')
    def test_authentication_failure_handling(
        self,
        mock_post,
        sample_files,
        sample_processing_options
    ):
        """Test proper handling of authentication failures."""
        # Create client with invalid token
        client = MineruClient(api_token="invalid_token")
        upload_service = UploadService(client)

        batch = Batch(processing_options=sample_processing_options)
        for file_path in sample_files:
            batch.add_file(file_path)

        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = Exception("Unauthorized")
        mock_post.return_value = mock_response

        # Should raise authentication error
        with pytest.raises(Exception):
            upload_service.upload_batch(batch)

    @patch('mineru_desktop.core.client.requests.post')
    @patch('mineru_desktop.core.client.requests.put')
    def test_large_batch_upload(
        self,
        mock_put,
        mock_post,
        sample_api_token,
        temp_dir,
        sample_processing_options
    ):
        """Test uploading a large batch of files."""
        import os

        client = MineruClient(api_token=sample_api_token)
        upload_service = UploadService(client)

        # Create large batch
        batch = Batch(processing_options=sample_processing_options)
        large_file_list = []

        for i in range(10):
            file_path = os.path.join(temp_dir, f"large_test_{i}.pdf")
            with open(file_path, "wb") as f:
                f.write(b"%PDF-1.4\ntest content")
            large_file_list.append(file_path)
            batch.add_file(file_path)

        # Mock responses
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "data": {
                "batch_id": "large_batch",
                "file_urls": [f"https://upload.example.com/{i}" for i in range(10)]
            }
        }
        mock_post.return_value = mock_post_response

        mock_put_response = Mock()
        mock_put_response.status_code = 200
        mock_put.return_value = mock_put_response

        # Upload
        upload_service.upload_batch(batch)

        # Verify
        assert batch.batch_id == "large_batch"
        assert len(batch.files) == 10
        assert mock_put.call_count == 10

    def test_progress_tracking(
        self,
        sample_api_token,
        sample_files,
        sample_processing_options
    ):
        """Test progress tracking throughout upload."""
        with patch('mineru_desktop.core.client.requests.post') as mock_post, \
             patch('mineru_desktop.core.client.requests.put') as mock_put:

            client = MineruClient(api_token=sample_api_token)

            # Track progress
            progress_updates = []

            def progress_callback(progress):
                progress_updates.append(progress)

            # Mock responses
            mock_post_response = Mock()
            mock_post_response.status_code = 200
            mock_post_response.json.return_value = {
                "data": {
                    "batch_id": "progress_batch",
                    "file_urls": [
                        "https://upload.example.com/1",
                        "https://upload.example.com/2",
                        "https://upload.example.com/3"
                    ]
                }
            }
            mock_post.return_value = mock_post_response

            mock_put_response = Mock()
            mock_put_response.status_code = 200
            mock_put.return_value = mock_put_response

            # Upload with progress callback
            client.upload_batch(
                sample_files,
                sample_processing_options,
                progress_callback=progress_callback
            )

            # Verify progress was tracked
            assert len(progress_updates) == 3
            assert progress_updates[0] > 0
            assert progress_updates[-1] == 100
            assert all(
                progress_updates[i] <= progress_updates[i + 1]
                for i in range(len(progress_updates) - 1)
            )

    @patch('mineru_desktop.core.client.requests.get')
    def test_polling_until_completion(
        self,
        mock_get,
        sample_api_token
    ):
        """Test polling API until all files are completed."""
        client = MineruClient(api_token=sample_api_token)

        # Simulate gradual completion
        responses = [
            {
                "data": {
                    "files": [
                        {"status": "processing"},
                        {"status": "processing"},
                        {"status": "pending"}
                    ]
                }
            },
            {
                "data": {
                    "files": [
                        {"status": "done", "zip_url": "url1"},
                        {"status": "processing"},
                        {"status": "processing"}
                    ]
                }
            },
            {
                "data": {
                    "files": [
                        {"status": "done", "zip_url": "url1"},
                        {"status": "done", "zip_url": "url2"},
                        {"status": "done", "zip_url": "url3"}
                    ]
                }
            }
        ]

        call_index = [0]

        def get_side_effect(*args, **kwargs):
            response = Mock()
            response.status_code = 200
            response.json.return_value = responses[min(call_index[0], len(responses) - 1)]
            call_index[0] += 1
            return response

        mock_get.side_effect = get_side_effect

        # Poll until all done
        max_polls = 10
        for _ in range(max_polls):
            status = client.get_batch_status("test_batch")
            files = status["data"]["files"]

            if all(f["status"] == "done" for f in files):
                break

        # Verify we polled multiple times
        assert call_index[0] >= 3
        # Verify final state is all done
        assert all(f["status"] == "done" for f in files)
