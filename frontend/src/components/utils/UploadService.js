import http from "./httpService";

class UploadService {
    upload(files, version, onUploadProgress) {
        let formData = new FormData();

        Array.from(files).map((file) => {
            formData.append("files", file);
            return undefined;
        });

        return http.post("/version/"+version+"/import", formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
            onUploadProgress,
        });
    }

    getFiles() {
        return http.get("/files");
    }
}

export default new UploadService();