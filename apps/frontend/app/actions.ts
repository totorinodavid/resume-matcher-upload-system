"use server";

import { signOut } from "@/auth";
import { redirect } from "next/navigation";

export async function doLogout() {
  await signOut({ 
    redirect: false 
  });
  redirect("/en/login");
}
