package com.example.OAuth.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {
    @GetMapping("public")
    public String login(){
        return "Authenticated";
    }
    @GetMapping("private")
    public String log(){
        return "Authorization";
    }

}
