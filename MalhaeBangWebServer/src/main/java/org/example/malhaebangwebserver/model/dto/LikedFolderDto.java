package org.example.malhaebangwebserver.model.dto;

import lombok.Getter;

@Getter
public class LikedFolderDto {
    private Integer folderId;
    private String folderName;

    public LikedFolderDto(Integer folderId, String folderName) {
        this.folderId = folderId;
        this.folderName = folderName;
    }

}